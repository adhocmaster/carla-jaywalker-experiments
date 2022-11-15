import logging

class ClientUser:
    
    def __init__(self, client):
        self.client = client


    @property
    def world(self):
        return self.client.get_world()

    @property
    def map(self):
        return self.world.get_map()

    @property
    def worldActors(self):
        return self.world.get_actors()

    @property
    def debug(self):
        return self.world.debug

    
    def error(self, msg):
        logging.error(msg)
        raise Exception(msg)
    
