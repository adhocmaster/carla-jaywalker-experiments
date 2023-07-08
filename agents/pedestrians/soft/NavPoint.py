class NavPoint:
    """
    """
    def __init__(self):
        self.laneId = None #lane id wrt the ego vehicle's direction. ego vehicle has left and right vehicles, where ego's lane has id 0. left is negative, right is positive.
        self.laneSection = None
        self.distanceToEgo = None


