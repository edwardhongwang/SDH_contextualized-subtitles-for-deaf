def log_options():
    return {
        "full": {
            "datefmt": "%Y-%m-%d_%H:%M:%S",
            "format": (
                "%(levelname)s : %(asctime)s : %(module)s : "
                "%(funcName)s : %(lineno)d -- %(message)s"
            )
        },
        "short": {
            "format": (
                "%(levelname)s : %(module)s : "
                "%(funcName)s -- %(message)s"
            )
        },
        "tiny": {
            "format": "%(levelname)s -- %(message)s"
        }
    }


