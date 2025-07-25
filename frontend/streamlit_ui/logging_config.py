import logging
import logging.config


def setup_logging(filename: str):
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "standard",
                "filename": f"{filename}.log",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    }

    logging.config.dictConfig(logging_config)
