import logging


class LoggerFactory:
    
    @staticmethod
    def create(name, config=None) -> logging.Logger:
        logger = logging.getLogger(name)
        if config is not None:
            if "LOG_LEVEL" in config:
                logger.setLevel(config["LOG_LEVEL"])
        return logger