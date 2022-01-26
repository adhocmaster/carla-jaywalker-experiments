import logging
from abc import abstractmethod


class LogProducer:

    @property
    @abstractmethod
    def logger(self):
        raise Exception("LogProducer - no logger")
    