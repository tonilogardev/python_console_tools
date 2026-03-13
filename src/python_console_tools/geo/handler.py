import numpy as np
import rasterio
from rasterio.windows import Window
import torch


class SatelliteImageHandler:
    """Windowed CRS-aware reading/writing for GeoTIFFs."""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_patch(self, row_off: int, col_off: int, width: int, height: int):
        with rasterio.open(self.filepath) as src:
            window = Window(col_off, row_off, width, height)
            data = src.read(window=window)
            window_transform = src.window_transform(window)
            profile = src.profile
            tensor = torch.from_numpy(data.astype(np.float32))
            return tensor, profile, window, window_transform

    def write_patch(self, output_path: str, tensor: torch.Tensor, profile: dict, window: Window | None = None, window_transform=None):
        data = tensor.cpu().numpy()
        out_profile = profile.copy()
        out_profile.update(dtype=data.dtype.name, count=data.shape[0])
        if window_transform is not None:
            out_profile.update(height=window.height, width=window.width, transform=window_transform)

        with rasterio.open(output_path, "w", **out_profile) as dst:
            if window is not None and window_transform is None:
                dst.write(data, window=window)
            else:
                dst.write(data)
