from abc import abstractmethod, ABC
from .ClientUser import ClientUser

class OnTicker(ClientUser):

    def __init__(self, client):
        super().__init__(client)

    @abstractmethod
    def onTick(self, world_snapshot):
        pass
