import logging
import logging.config
import pathlib
from typing import Any, Dict

import yaml


def configure_logging(config_path: pathlib.Path) -> None:
    \"\"\"Configure logging from a YAML file; fallback to basic config on error.\"\"\"

    if not config_path.exists():
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).warning("Logging config not found: %s", config_path)
        return

    with config_path.open("r", encoding="utf-8") as fp:
        config: Dict[str, Any] = yaml.safe_load(fp)

    _ensure_log_directory(config)
    logging.config.dictConfig(config)


def _ensure_log_directory(config: Dict[str, Any]) -> None:
    handlers = config.get("handlers", {})
    file_handler = handlers.get("file", {})
    filename = file_handler.get("filename")
    if filename:
        log_path = pathlib.Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)
