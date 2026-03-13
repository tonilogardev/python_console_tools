from python_console_tools.settings import Settings


class SeamService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create(self, name: str) -> None:
        # TODO: implement seam creation logic
        return None

    def search_north_south_seam(self, img_east: str, img_west: str, mask: str, out_dir: str, buffer_pixels: int = 15, block_size: int = 4096):
        from pathlib import Path
        from python_console_tools.seam.dijkstra import run_seam_pipeline

        return run_seam_pipeline(Path(img_east), Path(img_west), Path(mask), Path(out_dir), buffer_pixels=buffer_pixels, block_size=block_size)
