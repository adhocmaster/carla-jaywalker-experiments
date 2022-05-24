import carla
class DrunkenWalker(forceModel):
    def calculateFore(self):
        return carla.Vector3D(x=1, y=1, z=1)