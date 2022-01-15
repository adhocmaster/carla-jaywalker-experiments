class ClientUser:
    
    def __init__(self, client):
        self.client = client


    @property
    def world(self):
        return self.client.get_world()

    @property
    def map(self):
        return self.client.get_world().get_map()

    @property
    def debug(self):
        return self.world.debug
    
