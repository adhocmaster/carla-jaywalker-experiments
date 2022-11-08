import carla
from shapely.geometry import Polygon, LineString
from ..PedestrianAgent import PedestrianAgent
from lib import Geometry

class CrosswalkModel:

    def __init__(
            self, 
            agent: PedestrianAgent, 
            source: carla.Location, 
            idealDestination: carla.Location, 
            areaPolygon: Polygon=None, 
            goalLine: LineString=None,
            debug=False
        ):

        self.debug = debug
        self.visualizer = agent.visualizer
        self.agent = agent
        self.source = source
        self.idealDestination = idealDestination
        self.areaPolygon = areaPolygon
        self.goalLine = goalLine
        self.intermediatePoints = []
        self.finalDestination = None
        self.nextIntermediatePointIdx = None
        if self.areaPolygon == None:
            self.createPolygon()
        pass

    
    
    def createPolygon(self):
        
        centerScanLine = Geometry.makeCenterScanLine(self.source, self.idealDestination)
        # visualizer.drawShapelyLine(centerScanLine)
        scanLines, sideWalkPoints = Geometry.getScanLinesAndSidewalkPoints(self.agent.world, centerScanLine)

        if len(sideWalkPoints) < 2:
            self.agent.logger.error(f"Cannot create crosswalk area as there is # sidewalk points < 2")
            raise Exception(f"Cannot create crosswalk area as there is # sidewalk points < 2")


        # TODO: we make a generic one which may be based on real world dataset. Also create a goal line
        if self.goalLine == None:
            self.goalLine = LineString([sideWalkPoints[0], sideWalkPoints[-1]])
        
        self.areaPolygon = Polygon([Geometry.locationToPoint(self.source), sideWalkPoints[0], sideWalkPoints[-1]])
       
        if self.debug:
            self.visualizeScanLines(scanLines)
            self.visualizeSideWalkPoints(sideWalkPoints)
            self.visualizeArea()
        # self.areaPolygon = self.genPolyArea(self.source, self.idealDestination, self.goalLine)

    
    def visualizeScanLines(self, scanLines):
        count = 0
        for scanLine in scanLines: 
            count += 1
            self.visualizer.drawShapelyLine(scanLine, life_time=2.0, color=(50, count * 5, count * 5))

        pass


    def visualizeSideWalkPoints(self, sideWalkPoints):
        for sidewalkPoint in sideWalkPoints:
            self.visualizer.drawShaplyPoint(sidewalkPoint, color=(0, 100, 200), life_time=5.0)

    
    def visualizeArea(self):
        self.visualizer.drawShapelyPolygon(self.areaPolygon, color=(0, 100, 100, 100), life_time=10.0)


    def createGoalLine(self):
        goal = self.idealDestination
        #goalLine = shapely.LineString([goal.coords[0]-length, goal.coords[0]+length])
        #self.goalLine = goalLine
        # TODO: muktadir createGoalLine
        raise NotImplementedError("createGoalLine is not implemented")

    
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

        
    pass