from __future__ import annotations

import heapq
import logging
import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
from numba import njit
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
logger = logging.getLogger(__name__)

gdal.SetCacheMax(4 * 1024 * 1024 * 1024)  # 4 GB GDAL cache


def create_buffered_polygon(vec_in_path: Path, ref_img_path: Path, r008_name: str, r051_name: str, out_dir: Path, buffer_pixels: int = 15):
    ref_ds = gdal.Open(str(ref_img_path))
    if not ref_ds:
        raise RuntimeError(f"No se pudo abrir la imagen de referencia: {ref_img_path}")

    gt = ref_ds.GetGeoTransform()
    pixel_size = abs(gt[1])
    buffer_distance = pixel_size * buffer_pixels
    logger.info("Pixel size: %.3f m, buffer (%d px): %.3f m", pixel_size, buffer_pixels, buffer_distance)

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(ref_ds.GetProjection())

    geom_linestring = None
    if vec_in_path.suffix.lower() == ".msk":
        logger.info("Leyendo archivo .msk")
        geom_linestring = ogr.Geometry(ogr.wkbLineString)
        with vec_in_path.open("r") as f:
            lines = f.readlines()
            for line in lines[2:]:
                parts = line.strip().split(" ")
                if len(parts) >= 2:
                    coords = parts[1].split(",")
                    if len(coords) >= 2:
                        px_x = float(coords[0])
                        px_y = float(coords[1])
                        geom_linestring.AddPoint(px_x, px_y)
    else:
        logger.info("Leyendo vector (.shp/.gpkg)")
        vec_in = ogr.Open(str(vec_in_path))
        if not vec_in:
            raise RuntimeError(f"No se pudo abrir el vector de entrada: {vec_in_path}")
        layer_in = vec_in.GetLayer()
        spatial_ref = layer_in.GetSpatialRef() or spatial_ref
        feature_first = layer_in.GetFeature(0)
        if feature_first:
            geom_ref = feature_first.GetGeometryRef()
            if geom_ref and geom_ref.GetGeometryName() == "LINESTRING":
                geom_linestring = geom_ref.Clone()

    if not geom_linestring:
        raise RuntimeError("No se encontró una geometría LineString válida en el archivo de entrada.")

    out_shp_name = f"001_{r008_name}_{r051_name}.shp"
    out_shp_path = out_dir / out_shp_name
    shp_driver = ogr.GetDriverByName("ESRI Shapefile")
    if out_shp_path.exists():
        shp_driver.DeleteDataSource(str(out_shp_path))
    vec_out = shp_driver.CreateDataSource(str(out_shp_path))
    layer_out = vec_out.CreateLayer("corredor", spatial_ref, ogr.wkbPolygon)
    layer_out.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
    buffered_geom = geom_linestring.Buffer(buffer_distance)
    feature_out = ogr.Feature(layer_out.GetLayerDefn())
    feature_out.SetField("id", 1)
    feature_out.SetGeometry(buffered_geom)
    layer_out.CreateFeature(feature_out)
    vec_out = None
    logger.info("Buffer guardado en %s", out_shp_path.name)

    waypoints: list[Tuple[float, float]] = []
    point_count = geom_linestring.GetPointCount()
    if point_count > 0:
        num_wp = min(point_count, 10)
        indices = [int(i) for i in np.linspace(0, point_count - 1, num_wp)]
        for idx in indices:
            x, y, _ = geom_linestring.GetPoint(idx)
            waypoints.append((x, y))
        logger.info("Extraídos %d waypoints", len(waypoints))

    ref_ds = None
    return out_shp_path, waypoints


def compute_seam_dijkstra_constrained(cost_arr: np.ndarray, start_r: int, start_c: int, end_r: int, end_c: int):
    rows, cols = cost_arr.shape
    pq: list[tuple[float, int, int]] = []
    dist = {}
    prev = {}

    start_cost = 99999.0 if cost_arr[start_r, start_c] == 255 else float(cost_arr[start_r, start_c])
    dist[(start_r, start_c)] = start_cost
    prev[(start_r, start_c)] = None
    heapq.heappush(pq, (start_cost, start_r, start_c))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    end_node = None

    while pq:
        d, r, c = heapq.heappop(pq)
        if abs(r - end_r) <= 1 and abs(c - end_c) <= 1:
            end_node = (r, c)
            break
        if d > dist.get((r, c), float("inf")):
            continue
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                val = cost_arr[nr, nc]
                step_cost = 99999.0 if val == 255 else float(val)
                new_dist = d + step_cost
                if new_dist < dist.get((nr, nc), float("inf")):
                    dist[(nr, nc)] = new_dist
                    prev[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (new_dist, nr, nc))

    path = []
    if end_node:
        curr = end_node
        while curr is not None:
            path.append(curr)
            curr = prev.get(curr)
        path.reverse()
    return path


def rasterize_clip_and_mosaic(vec_path: Path, img_r008: Path, img_r051: Path, name_r008: str, name_r051: str, base_name: str, waypoints: list[tuple[float, float]], out_dir: Path, block_size: int = 4096) -> bool:
    drv = gdal.GetDriverByName("GTiff")

    ref_ds = gdal.Open(str(img_r051))
    if not ref_ds:
        raise RuntimeError(f"No se pudo abrir {img_r051}")
    w, h = ref_ds.RasterXSize, ref_ds.RasterYSize
    gt = ref_ds.GetGeoTransform()
    proj = ref_ds.GetProjection()
    num_bands = ref_ds.RasterCount
    data_type = ref_ds.GetRasterBand(1).DataType
    ref_ds = None

    out_mask_path = out_dir / f"{base_name}_mask.tif"
    vec_ds = ogr.Open(str(vec_path))
    layer = vec_ds.GetLayer()
    mask_ds = drv.Create(str(out_mask_path), w, h, 1, gdal.GDT_Byte, options=["COMPRESS=DEFLATE"])
    mask_ds.SetGeoTransform(gt)
    mask_ds.SetProjection(proj)
    mask_ds.GetRasterBand(1).Fill(0)
    gdal.RasterizeLayer(mask_ds, [1], layer, burn_values=[1])
    mask_ds = None
    vec_ds = None

    bbox = [gt[0], gt[3] + h * gt[5], gt[0] + w * gt[1], gt[3]]

    def warp_clip_blocks(src_path: Path, out_path: Path):
        creation_ops = ["COMPRESS=DEFLATE", "BIGTIFF=YES", "TILED=YES"]
        if num_bands == 3 and data_type == gdal.GDT_Byte:
            creation_ops.append("PHOTOMETRIC=RGB")
        temp_ds = drv.Create(str(out_path), w, h, num_bands, data_type, options=creation_ops)
        temp_ds.SetGeoTransform(gt)
        temp_ds.SetProjection(proj)
        vrt_opts = gdal.WarpOptions(format="VRT", outputBounds=bbox, width=w, height=h, resampleAlg=gdal.GRA_NearestNeighbour)
        src_vrt = gdal.Warp("", str(src_path), options=vrt_opts)
        m_ds = gdal.Open(str(out_mask_path))
        for y in range(0, h, block_size):
            for x in range(0, w, block_size):
                y_size = min(block_size, h - y)
                x_size = min(block_size, w - x)
                mask_chunk = m_ds.GetRasterBand(1).ReadAsArray(x, y, x_size, y_size)
                for b_idx in range(1, num_bands + 1):
                    arr_chunk = src_vrt.GetRasterBand(b_idx).ReadAsArray(x, y, x_size, y_size)
                    arr_chunk[mask_chunk == 0] = 0
                    temp_ds.GetRasterBand(b_idx).WriteArray(arr_chunk, x, y)
                mask_chunk = None
        for b_idx in range(1, num_bands + 1):
            temp_ds.GetRasterBand(b_idx).SetNoDataValue(0)
        temp_ds = None

    out_r051_path = out_dir / f"002_{name_r051}_cut_mask.tif"
    warp_clip_blocks(img_r051, out_r051_path)
    out_r008_path = out_dir / f"003_{name_r008}_cut_mask.tif"
    warp_clip_blocks(img_r008, out_r008_path)

    out_diff_path = out_dir / f"004_{name_r008}_{name_r051}_img_dif.tif"
    diff_ds = drv.Create(str(out_diff_path), w, h, 1, gdal.GDT_Byte, options=["COMPRESS=DEFLATE"])
    diff_ds.SetGeoTransform(gt)
    diff_ds.SetProjection(proj)
    ds_1 = gdal.Open(str(out_r051_path))
    ds_2 = gdal.Open(str(out_r008_path))
    m_ds = gdal.Open(str(out_mask_path))
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            y_size = min(block_size, h - y)
            x_size = min(block_size, w - x)
            mask_chunk = m_ds.GetRasterBand(1).ReadAsArray(x, y, x_size, y_size)
            if num_bands == 1:
                chunk_1 = ds_1.GetRasterBand(1).ReadAsArray(x, y, x_size, y_size).astype(np.float32)
                chunk_2 = ds_2.GetRasterBand(1).ReadAsArray(x, y, x_size, y_size).astype(np.float32)
                diff_chunk = np.abs(chunk_1 - chunk_2).astype(np.uint8)
            else:
                sum_diff = np.zeros((y_size, x_size), dtype=np.float32)
                for b_idx in range(1, num_bands + 1):
                    chunk_1 = ds_1.GetRasterBand(b_idx).ReadAsArray(x, y, x_size, y_size).astype(np.float32)
                    chunk_2 = ds_2.GetRasterBand(b_idx).ReadAsArray(x, y, x_size, y_size).astype(np.float32)
                    sum_diff += np.abs(chunk_1 - chunk_2)
                diff_chunk = (sum_diff / num_bands).astype(np.uint8)
            diff_chunk[mask_chunk == 0] = 255
            diff_ds.GetRasterBand(1).WriteArray(diff_chunk, x, y)
    diff_ds.FlushCache()
    diff_mean = diff_ds.GetRasterBand(1).ReadAsArray()
    diff_ds = None
    ds_1 = None
    ds_2 = None
    m_ds = None

    if not waypoints or len(waypoints) < 2:
        raise RuntimeError("No se han encontrado suficientes coordenadas en el archivo.")

    waypoints_grid = []
    for pt in waypoints:
        c = int(round((pt[0] - gt[0]) / gt[1]))
        r = int(round((pt[1] - gt[3]) / gt[5]))
        c = max(0, min(w - 1, c))
        r = max(0, min(h - 1, r))
        waypoints_grid.append((r, c))

    path_dijk = []
    for i in range(len(waypoints_grid) - 1):
        start_r, start_c = waypoints_grid[i]
        end_r, end_c = waypoints_grid[i + 1]
        segment_path = compute_seam_dijkstra_constrained(diff_mean, start_r, start_c, end_r, end_c)
        if not segment_path:
            raise RuntimeError("Fallo al calcular un tramo de la órbita.")
        if i < len(waypoints_grid) - 2:
            path_dijk.extend(segment_path[:-1])
        else:
            path_dijk.extend(segment_path)

    out_msk_path = out_dir / f"005_{name_r008}_{name_r051}_seamline_DIJK.msk"
    origin_x, origin_y = gt[0], gt[3]
    pixel_x, pixel_y = gt[1], abs(gt[5])
    with out_msk_path.open("w") as f:
        f.write(f"{origin_x:.6f},{origin_y:.6f} {pixel_x:.6f},{pixel_y:.6f}\n")
        f.write(f"65280 {len(path_dijk)}\n")
        for r_abs, c_abs in path_dijk:
            px_x = gt[0] + c_abs * gt[1] + r_abs * gt[2]
            px_y = gt[3] + c_abs * gt[4] + r_abs * gt[5]
            f.write(f"{c_abs},{r_abs} {px_x:.6f},{px_y:.6f}\n")

    ds_w = gdal.Open(str(img_r051))
    gt_w = ds_w.GetGeoTransform()
    minx_w = gt_w[0]
    maxy_w = gt_w[3]
    maxx_w = minx_w + gt_w[1] * ds_w.RasterXSize
    miny_w = maxy_w + gt_w[5] * ds_w.RasterYSize
    ds_w = None

    ds_e = gdal.Open(str(img_r008))
    gt_e = ds_e.GetGeoTransform()
    minx_e = gt_e[0]
    maxy_e = gt_e[3]
    maxx_e = minx_e + gt_e[1] * ds_e.RasterXSize
    miny_e = maxy_e + gt_e[5] * ds_e.RasterYSize
    ds_e = None

    minx = min(minx_w, minx_e)
    maxy = max(maxy_w, maxy_e)
    maxx = max(maxx_w, maxx_e)
    miny = min(miny_w, miny_e)

    pixel_size_x = gt_w[1]
    pixel_size_y = gt_w[5]
    w_full = int(round((maxx - minx) / pixel_size_x))
    h_full = int(round((miny - maxy) / pixel_size_y))
    gt_full = (minx, pixel_size_x, 0, maxy, 0, pixel_size_y)

    path_full = []
    for r, c in path_dijk:
        px_x = gt[0] + c * gt[1] + r * gt[2]
        px_y = gt[3] + c * gt[4] + r * gt[5]
        c_full = int(round((px_x - gt_full[0]) / gt_full[1]))
        r_full = int(round((px_y - gt_full[3]) / gt_full[5]))
        path_full.append((r_full, c_full))

    mask_r051_full = np.ones((h_full, w_full), dtype=bool)
    if path_full:
        min_r = min(r for r, _ in path_full)
        max_r = max(r for r, _ in path_full)
        first_c = next(c for r, c in path_full if r == min_r)
        for r in range(0, min_r):
            mask_r051_full[r, first_c:] = False
        for r, c in path_full:
            mask_r051_full[r, c:] = False
        last_c = next(c for r, c in reversed(path_full) if r == max_r)
        for r in range(max_r + 1, h_full):
            mask_r051_full[r, last_c:] = False

    mask_r008_full = ~mask_r051_full

    out_mask_w = out_dir / f"006a_{name_r051}_west_mask.tif"
    out_mask_e = out_dir / f"006b_{name_r008}_east_mask.tif"

    ds_w = drv.Create(str(out_mask_w), w_full, h_full, 1, gdal.GDT_Byte, options=["COMPRESS=DEFLATE", "NBITS=1"])
    ds_w.SetGeoTransform(gt_full)
    ds_w.SetProjection(proj)
    ds_w.GetRasterBand(1).WriteArray(mask_r051_full.astype(np.uint8))
    ds_w = None

    ds_e = drv.Create(str(out_mask_e), w_full, h_full, 1, gdal.GDT_Byte, options=["COMPRESS=DEFLATE", "NBITS=1"])
    ds_e.SetGeoTransform(gt_full)
    ds_e.SetProjection(proj)
    ds_e.GetRasterBand(1).WriteArray(mask_r008_full.astype(np.uint8))
    ds_e = None

    vrt_opts = gdal.WarpOptions(
        format="VRT",
        outputBounds=(gt_full[0], gt_full[3] + h_full * gt_full[5], gt_full[0] + w_full * gt_full[1], gt_full[3]),
        xRes=gt_full[1],
        yRes=abs(gt_full[5]),
        dstSRS=proj,
        resampleAlg=gdal.GRA_NearestNeighbour,
    )
    vrt_r051 = gdal.Warp("", str(img_r051), options=vrt_opts)
    vrt_r008 = gdal.Warp("", str(img_r008), options=vrt_opts)

    out_mosaic_path = out_dir / f"007_{name_r008}_{name_r051}_mosaico_final.tif"
    creation_ops = ["COMPRESS=DEFLATE", "TILED=YES", "BIGTIFF=YES", "PREDICTOR=2"]
    if num_bands == 3 and data_type == gdal.GDT_Byte:
        creation_ops.append("PHOTOMETRIC=RGB")

    out_ds = drv.Create(str(out_mosaic_path), w_full, h_full, num_bands, data_type, options=creation_ops)
    out_ds.SetGeoTransform(gt_full)
    out_ds.SetProjection(proj)
    for b in range(1, num_bands + 1):
        out_ds.GetRasterBand(b).SetNoDataValue(0)

    for y in range(0, h_full, block_size):
        for x in range(0, w_full, block_size):
            y_size = min(block_size, h_full - y)
            x_size = min(block_size, w_full - x)
            mask_w_chunk = mask_r051_full[y : y + y_size, x : x + x_size]
            mask_e_chunk = mask_r008_full[y : y + y_size, x : x + x_size]
            for b_idx in range(1, num_bands + 1):
                chunk_51 = vrt_r051.GetRasterBand(b_idx).ReadAsArray(x, y, x_size, y_size)
                chunk_08 = vrt_r008.GetRasterBand(b_idx).ReadAsArray(x, y, x_size, y_size)
                merged = np.zeros((y_size, x_size), dtype=chunk_51.dtype)
                merged[mask_w_chunk] = chunk_51[mask_w_chunk]
                merged[mask_e_chunk] = chunk_08[mask_e_chunk]
                empty_mask = merged == 0
                valid_51 = chunk_51 != 0
                merged[empty_mask & valid_51] = chunk_51[empty_mask & valid_51]
                empty_mask = merged == 0
                valid_08 = chunk_08 != 0
                merged[empty_mask & valid_08] = chunk_08[empty_mask & valid_08]
                out_ds.GetRasterBand(b_idx).WriteArray(merged, x, y)

    out_ds = None
    vrt_r051 = None
    vrt_r008 = None
    return True, out_mosaic_path


def run_seam_pipeline(img_east: Path, img_west: Path, mask_path: Path, out_dir: Path, buffer_pixels: int = 15, block_size: int = 4096):
    out_dir.mkdir(parents=True, exist_ok=True)
    name_r008 = img_east.stem
    name_r051 = img_west.stem
    out_shp_path, waypoints = create_buffered_polygon(mask_path, img_east, name_r008, name_r051, out_dir, buffer_pixels=buffer_pixels)
    ok, mosaic = rasterize_clip_and_mosaic(out_shp_path, img_east, img_west, name_r008, name_r051, f"001_{name_r008}_{name_r051}", waypoints, out_dir, block_size=block_size)
    return ok, mosaic
