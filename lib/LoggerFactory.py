import logging


class LoggerFactory:

    fileHandler = None
    streamHandler = None
    formatter = None
    defaultLevel = None
    
    @staticmethod
    def createBaseLogger(name, defaultLevel=logging.INFO, file=None):
        LoggerFactory.defaultLevel = defaultLevel

        logger = logging.getLogger(name)
        logger.setLevel(LoggerFactory.defaultLevel)

        LoggerFactory.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if file is not None:
            # create file handler for logger.
            LoggerFactory.fileHandler = logging.FileHandler(file)
            LoggerFactory.fileHandler.setLevel(level=LoggerFactory.defaultLevel)
            LoggerFactory.fileHandler.setFormatter(LoggerFactory.formatter)

        # create console handler for logger.
        LoggerFactory.streamHandler = logging.StreamHandler()
        LoggerFactory.streamHandler.setLevel(level=LoggerFactory.defaultLevel)
        LoggerFactory.streamHandler.setFormatter(LoggerFactory.formatter)

        if file is not None:
            logger.addHandler(LoggerFactory.fileHandler)
        logger.addHandler(LoggerFactory.streamHandler)

        return logger




    @staticmethod
    def create(name, config=None) -> logging.Logger:

        print(f"creating {name} logger")

        logger = logging.getLogger(name)

        if config is not None and "LOG_LEVEL" in config:
            logger.setLevel(config["LOG_LEVEL"])

        elif LoggerFactory.defaultLevel is not None:
            logger.setLevel(LoggerFactory.defaultLevel)

        else:
            logger.setLevel(logging.INFO)

        if LoggerFactory.fileHandler is not None:
            logger.addHandler(LoggerFactory.fileHandler)

        if LoggerFactory.streamHandler is not None:
            print("Setting console logger")
            logger.addHandler(LoggerFactory.streamHandler)

        
        return logger

    