
import carla
from typing import List

class ObstacleManager:

    """Every agent has their own instance of the obstacle manager
    """

    def __init__(self, actor: carla.Actor):
        
        self._actor = actor
        self._world = actor.get_world()
        self._map = self.world.get_map()
        self._cache = {}

    @property
    def actor(self):
        return self._actor

    @property
    def map(self):
        return self._map

    @property
    def world(self):
        return self._world

    
    def obstacleIn(self, obstacles: List[carla.LabelledPoint], obstacle: carla.LabelledPoint):
        if obstacle in obstacles:
            return True
        
        for existing in obstacles:
            if existing.location == obstacle.location:
                return True
        return False

    def unionToA(self, obstaclesA: List[carla.LabelledPoint], obstaclesB: List[carla.LabelledPoint]):
        for obstacle in obstaclesB:
            if self.obstacleIn(obstaclesA, obstacle) == False:
                obstaclesA.append(obstacle)
        

    def getFirstObstacleInADirection(self, centers: List[carla.Location], direction: carla.Vector3D, distance: float) -> List[carla.LabelledPoint]:
        """[summary]

        Args:
            centers (List[carla.Location]): [description] at least 2 coordinates with 2 z values.
            direction (carla.Vector3D): [description]
            distance (float): [description]

        Returns:
            List[carla.LabelledPoint]: [description]
        """
        lbs = []
        for center in centers:
            lb = self.world.project_point(center, direction, distance)
            if self.obstacleIn(lbs, lb) == False:
                lbs.append(lb)
            
        return lbs


    def getAllObstaclesInADirection(self, centers: List[carla.Location], direction: carla.Vector3D, distance: float) -> List[carla.LabelledPoint]:

        distanceVector = direction * distance
        lbs = []
        for center in centers:
            destination = carla.Location(
                x = center.x,
                y = center.y,
                z = center.z
            )

            self.unionToA(lbs, self.world.cast_ray(center, destination))
        
        return lbs


    def isSidewalk(self, actor):
        if 8 in actor.semantic_tags:
            return True
        return False


    
