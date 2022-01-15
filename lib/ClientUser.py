class ClientUser:
    
    def __init__(self, client):
        self.client = client
        self.world = client.get_world()
        self.map = self.world.get_map()

    
    def refreshClient(self):
        self.world = self.client.get_world()
        self.map = self.world.get_map()