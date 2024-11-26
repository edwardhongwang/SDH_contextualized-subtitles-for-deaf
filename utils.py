"""
Utility functions and helper methods.
"""
import yaml
import logging
import logging.config


# Logging setup
def setup_logger(config_folder=None):
    config = None
    try:
        if config_folder is not None:
            config_path = config_folder / "logging.yaml"
            config = yaml.safe_load(open(config_path))
    except FileNotFoundError:
        pass
    # Configure logging
    logging.config.dictConfig({
        "version": 1,
        "root":{
            "handlers" : ["console"],
            "level": "WARNING"
        },
        "handlers":{
            "console":{
                "formatter": "full",
                "class": "logging.StreamHandler"
            }
        },
        "formatters":{
            "full": {
                "datefmt":"%d-%m-%Y %I:%M:%S",
                "format": "%(levelname)s : %(asctime)s : %(module)s : %(funcName)s : %(lineno)d -- %(message)s",
            },
            "short": {
                "format": "%(levelname)s : %(module)s : %(funcName)s -- %(message)s"
            },
            "tiny": {
                "format": "%(levelname)s -- %(message)s"
            }
        },
        **config
    })
    logging.root.setLevel(
        logging.getLogger().getEffectiveLevel()
    )


# Performance monitoring
def monitor_performance(func):
    # Decorator for performance tracking
    pass
