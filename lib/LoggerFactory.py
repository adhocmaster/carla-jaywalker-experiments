import logging
from logging.handlers import TimedRotatingFileHandler

class LoggerFactory:

    fileHandler = None
    streamHandler = None
    formatter = None
    defaultLevel = None
    file = None
    
    @staticmethod
    def createBaseLogger(name, defaultLevel=logging.INFO, file=None):
        LoggerFactory.defaultLevel = defaultLevel
        LoggerFactory.file = file

        logger = logging.getLogger(name)
        logger.setLevel(LoggerFactory.defaultLevel)

        LoggerFactory.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if file is not None:
            with open(file, "w") as f:
                f.truncate(0)

            # create file handler for logger.
            LoggerFactory.fileHandler = logging.FileHandler(file)
            # LoggerFactory.fileHandler = TimedRotatingFileHandler(filename=file, when='midnight', backupCount=5)
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

        logger = logging.getLogger(name)
        level = None

        if config is not None and "LOG_LEVEL" in config:
            print(f"setting log level {config['LOG_LEVEL']} for {name}")
            logger.setLevel(config["LOG_LEVEL"])
            level = config["LOG_LEVEL"]

        elif LoggerFactory.defaultLevel is not None:
            print(f"setting log level {LoggerFactory.defaultLevel} for {name}")
            logger.setLevel(LoggerFactory.defaultLevel)
            level = LoggerFactory.defaultLevel

        else:
            print(f"setting log level {logging.INFO} for {name}")
            logger.setLevel(logging.INFO)
            level = logging.INFO

        if LoggerFactory.file is not None:

            # create file handler for logger.
            fileHandler = logging.FileHandler(LoggerFactory.file)
            # LoggerFactory.fileHandler = TimedRotatingFileHandler(filename=file, when='midnight', backupCount=5)
            fileHandler.setLevel(level=level)
            fileHandler.setFormatter(LoggerFactory.formatter)
            logger.addHandler(fileHandler)

        # create console handler for logger.
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(level=level)
        streamHandler.setFormatter(LoggerFactory.formatter)
        logger.addHandler(streamHandler)

        
        return logger

    