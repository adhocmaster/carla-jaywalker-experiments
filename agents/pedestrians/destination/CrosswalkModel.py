import carla
import shapely

class CrosswalkModel:
    def __init__(self, source, idealDestination, areaPolygon=None, goalLine=None):
        self.source = source
        self.idealDestination = idealDestination
        self.areaPolygon = areaPolygon
        self.goalLine = goalLine
        self.intermediatePoints = []
        self.finalDestination = None
        self.nextIntermediatePointIdx = None
        self.createPolygonIfNone()
        self.generateIntermediatePoints()
    
    def createPolygonIfNone(self):
        # TODO: we make a generic one which may be based on real world dataset. Also create a goal line
        if self.goalLine == None:
            self.createGoalLine(4)
        start_x, start_y = self.source.coords[0][0], self.source.coords[0][1]
        goalLine_x1, goalLine_y1 = self.goalLine.coords[0][0], self.goalLine.coords[0][1] 
        goalLine_x2, goalLine_y2 = self.goalLine.coords[1][0], self.goalLine.coords[1][1]
        # Bottom left point
        botLeft_x = start_x - 0.5
        botLeft_y = start_y
        botLeft = shapely.Point((botLeft_x, botLeft_y))
        # Bottom right point
        botRight_x = start_x + 0.5
        botRight_y = start_y
        botRight = shapely.Point((botRight_x, botRight_y))
        # Top left point
        topLeft_x = goalLine_x1
        topLeft_y = goalLine_y1
        topLeft = shapely.Point((topLeft_x, topLeft_y))
        # Top right point
        topRight_x = goalLine_x2
        topRight_y = goalLine_y2
        topRight = shapely.Point((topRight_x, topRight_y))
        # Mid left point
        midLeft_x = min(botLeft_x, topLeft_x) + (max(botLeft_x, topLeft_x) - min(botLeft_x, topLeft_x))/1.5
        midLeft_y = (topLeft_y - botLeft_y)/2
        midLeft = shapely.Point((midLeft_x, midLeft_y))
        # Mid right point
        midRight_x = min(botRight_x, topRight_x) + (max(botRight_x, topRight_x) - min(botRight_x, topRight_x))/3
        midRight_y = (topRight_y - botRight_y) / 2
        midRight = shapely.Point((midRight_x, midRight_y))
        # Build areaPolygon
        areaPolygon = shapely.Polygon([botLeft, midLeft, topLeft, topRight, midRight, botRight])
        self.areaPolygon = areaPolygon

    def createGoalLine(self, length):
        goal = self.idealDestination
        goalLine = shapely.LineString([goal.coords[0]-length, goal.coords[0]+length])
        self.goalLine = goalLine


    def generateIntermediatePoints(self):
        # TODO
        # 1. find the points

        # 2. set nextIntermediatePoint to the first one
        self.nextIntermediatePointIdx = 0

        # 3. set self.finalDestination

        pass


    def getNextDestinationPoint(self, agentLocation: carla.Location):
        # TODO
        # find if the pedestrian reached the local y coordinate with a threshold around 100 cm
        # change next destination point to the next intermediate point return 

        if self.hasReachedNextDestinationPoint(agentLocation):
            if self.nextIntermediatePointIdx == len(self.intermediatePoints) - 1:
                return self.finalDestination
            self.nextIntermediatePoint += 1 # this might overflow if we have reached the final 
        
        return self.intermediatePoints[self.nextIntermediatePointIdx]

    
    def hasReachedNextDestinationPoint(self, agentLocation: carla.Location):
        # TODO: fill it out
        return False
