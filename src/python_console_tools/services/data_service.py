from python_console_tools.settings import Settings


class DataService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def download_copernicus(self, region: str, from_date: str, to_date: str, product: str) -> None:
        # TODO: implement Copernicus download logic
        return None
