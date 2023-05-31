import carla
from shapely.geometry import Polygon, LineString
from ..PedestrianAgent import PedestrianAgent
from agents.pedestrians.factors import InternalFactors
from lib import Geometry, Utils
from .CrosswalkGeometry import CrosswalkGeometry
import numpy as np

class CrosswalkModel:

    def __init__(
            self, 
            agent: PedestrianAgent, 
            internalFactors: InternalFactors, 
            source: carla.Location, 
            idealDestination: carla.Location, 
            areaPolygon: Polygon=None, 
            goalLine: LineString=None,
            debug=False
        ):

        self.internalFactors = internalFactors

        self.debug = debug
        self.visualizer = agent.visualizer
        self.agent = agent
        self.source = source
        self.idealDestination = idealDestination
        self.areaPolygon = areaPolygon
        self.goalLine = goalLine

        self.crosswalkGeometry = None
        self.intermediatePoints = []
        self.finalDestination = None
        self.nextIntermediatePointIdx = None

        if self.areaPolygon == None:
            self.createPolygon()

        if ("use_random_destination_without_intermediates" in self.internalFactors) and (not self.internalFactors["use_random_destination_without_intermediates"]):
            self.__initGeomery()
        else:
            self.__setRandomDestination()

        pass

    
    def __initGeomery(self):
        self.crosswalkGeometry = CrosswalkGeometry(
            source=Geometry.locationToPoint(self.source),
            idealDestination=Geometry.locationToPoint(self.idealDestination),
            areaPolygon=self.areaPolygon,
            goalLine=self.goalLine
        )

        self.intermediatePoints = [carla.Location(point.x, point.y) for point in self.crosswalkGeometry.generateIntermediatePoints() ]
        self.nextIntermediatePointIdx = 0
        self.finalDestination = self.intermediatePoints[-1]

        if self.debug:
            # self.visualizer.drawPoints(self.intermediatePoints, life_time=5.0)
            self.visualizer.drawWalkerNavigationPoints(self.intermediatePoints, size=0.1, z=1.0, color=(0, 255, 255), coords=False, life_time=15.0)
    
    def __setRandomDestination(self):

        randomDestination = self.goalLine.interpolate(np.random.uniform(0, 1), normalized=True)
        self.intermediatePoints = [carla.Location(randomDestination.x, randomDestination.y)]
        self.nextIntermediatePointIdx = 0
        self.finalDestination = self.intermediatePoints[-1]

        if self.debug:
            self.visualizer.drawPoints(self.intermediatePoints, life_time=20.0)

    def getFinalDestination(self):
        return self.finalDestination


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
            # self.visualizeScanLines(scanLines)
            self.visualizeSideWalkPoints(sideWalkPoints)
            self.visualizeArea()

    
    def visualizeScanLines(self, scanLines):
        count = 0
        for scanLine in scanLines: 
            count += 1
            # self.visualizer.drawShapelyLine(scanLine, color=(count * 2, count * 2, count * 2), life_time=2.0)
            self.visualizer.drawShapelyLine(scanLine, color=(0, 0, 0, 255), life_time=1.0)

        pass


    def visualizeSideWalkPoints(self, sideWalkPoints):
        for sidewalkPoint in sideWalkPoints:
            self.visualizer.drawShaplyPoint(sidewalkPoint, color=(1, 1, 1), size=0.05, life_time=10.0)

    
    def visualizeArea(self):
        self.visualizer.drawShapelyPolygon(self.areaPolygon, color=(0, 0, 0, 255), life_time=10.0)

    
    def getNextDestinationPoint(self):
        # TODO
        # find if the pedestrian reached the local y coordinate with a threshold around 100 cm
        # change next destination point to the next intermediate point return 
        if self.hasReachedNextDestinationPoint(self.agent.location):
            if self.nextIntermediatePointIdx == len(self.intermediatePoints) - 1:
                self.agent.logger.info(f"going to the final destination")
                d =  self.agent.location.distance_2d(self.finalDestination)
                self.agent.logger.info(f"distance to next destination {d} meters")
                return self.finalDestination
            self.nextIntermediatePointIdx += 1 # this might overflow if we have reached the final 
        
        return self.intermediatePoints[self.nextIntermediatePointIdx]

    
    def hasReachedNextDestinationPoint(self, agentLocation: carla.Location):
        # TODO: fill it out
        nextDest = self.intermediatePoints[self.nextIntermediatePointIdx]

        return self.agent.hasReachedDestinationAlongLocalY(nextDest, 0.5)
        
    pass