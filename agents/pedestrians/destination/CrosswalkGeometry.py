from shapely.affinity import rotate
from shapely.geometry import LineString, Point, Polygon
import math
import random

class CrosswalkGeometry:
    '''
    CONSTANTS:
        MAX_ABSOLUTE_DEGREE: float
        MAX_RELATIVE_DEGREE: float
        INTER_POINTS_NUM: int
        INTER_POINTS_DISTANCE_MOD: float
    '''
    MAX_ABSOLUTE_DEGREE = math.radians(60)
    MAX_RELATIVE_DEGREE = math.radians(45)
    INTER_POINTS_NUM = 3
    INTER_POINTS_DISTANCE_MOD = 1.5

    def __init__(self, source: Point, idealDestination: Point, areaPolygon: Polygon=None, goalLine: LineString=None):
        self.source = source
        self.idealDestination = idealDestination
        self.areaPolygon = areaPolygon
        self.goalLine = goalLine
        self.intermediatePoints = []
        self.finalDestination = None
        self.nextIntermediatePointIdx = None
        if self.areaPolygon == None:
            self.createPolygonIfNone()
        self.generateIntermediatePoints()
    
    def createPolygonIfNone(self):
        # TODO: we make a generic one which may be based on real world dataset. Also create a goal line
        if self.goalLine == None:
            self.createGoalLine(4)
       
        self.areaPolygon = self.genPolyArea(self.source, self.idealDestination, self.goalLine)


    def genPolyArea(self, start: Point, end: Point, goalLine: LineString):
        '''
        Generate a generic areaPolygon given a start point, end point and a goalLine.
        
        Args:
            start (shapely.geometry.Point): the point where the pedestrian enters the crosswalk.
            end (shapely.geometry.Point): the ideal point where the pedestrian exits the crosswalk.
            goalLine (shapely.geometry.LineString): the sidewalk which contains the end point.

        Returns:
            areaPolygon (shapely.geometry.Polygon): the generated polygon that forms the area of an abstract crosswalk space.
        '''
        # Extract goalLine information
        goalLine_x1, goalLine_y1 = goalLine.coords[0][0], goalLine.coords[0][1] 
        goalLine_x2, goalLine_y2 = goalLine.coords[1][0], goalLine.coords[1][1]
        # Generate base as perpendicular to the vertical line
        verticalLine = LineString([start, end])
        baseRight = rotate(verticalLine, -90, origin=start)
        baseLeft = rotate(verticalLine, 90, origin=start)
        # Bottom left point
        botLeft = baseLeft.interpolate(0.5, normalized=False)
        botLeft_x = botLeft.coords[0][0]
        botLeft_y = botLeft.coords[0][1]
        # Bottom right point
        botRight = baseRight.interpolate(0.5, normalized=False)
        botRight_x = botRight.coords[0][0]
        botRight_y = botRight.coords[0][1]
        # Top left point
        topLeft_x = goalLine_x1
        topLeft_y = goalLine_y1
        topLeft = Point((topLeft_x, topLeft_y))
        # Top right point
        topRight_x = goalLine_x2
        topRight_y = goalLine_y2
        topRight = Point((topRight_x, topRight_y))
        # Mid left point
        midLeft_x = min(botLeft_x, topLeft_x) + (max(botLeft_x, topLeft_x) - min(botLeft_x, topLeft_x))/1.5
        midLeft_y = (topLeft_y - botLeft_y)/2
        midLeft = Point((midLeft_x, midLeft_y))
        # Mid right point
        midRight_x = min(botRight_x, topRight_x) + (max(botRight_x, topRight_x) - min(botRight_x, topRight_x))/3
        midRight_y = (topRight_y - botRight_y) / 2
        midRight = Point((midRight_x, midRight_y))

        # Build areaPolygon
        areaPolygon = Polygon([botLeft, midLeft, topLeft, topRight, midRight, botRight])
        return areaPolygon


    def generateIntermediatePoints(self, maxAbsDegree=MAX_ABSOLUTE_DEGREE, maxDeltaDegree=MAX_RELATIVE_DEGREE, nInterPoints=INTER_POINTS_NUM, maxInterPointsDistance=INTER_POINTS_DISTANCE_MOD):
        '''
        Generate intermediate points inside the crosswalk area to form pedestrian crossing trajectories. 

        Args:
            maxAbsDegree (float): the maximum degree between the new line and the vertical line that shares the same start point
            maxDeltaDegree (float): the maximum degree between the new line and the extended previous line. The end point of the previous line is the start point of the new line
            nInterPoints (int): the number of intermediates points to be generated
            maxInterPointsDistance (float): the scalar modifier for the max distance between any two intermediate points

        Returns:
            None
        '''
        start = self.source
        end = self.idealDestination
        crosswalk = self.areaPolygon
        goalLine = self.goalLine
        new_points = [start]
        pointsOL = self.pointsOnLine(start, end, nInterPoints)
        for i in range(len(pointsOL) - 2):
            start = pointsOL[1]
            end = pointsOL[2]
            done = False
            while not done:
                chance = random.choice([0, 1])
                pointToRot = self.pointBetween(start, end, d=random.uniform(0, 1)) # modify d if needed
                if chance == 0:
                    new_point = self.pointRotate(pointToRot, start, degree=90)
                    
                else:
                    new_point = self.pointRotate(pointToRot, start, degree=-90)
                # Check constraints
                if crosswalk.contains(new_point):
                    segment = LineString([start, end])
                    new_line = LineString([new_points[-1], new_point])
                    prev_line = None
                    if i > 0:
                        prev_line = LineString([new_points[-2], new_points[-1]])
                    if new_line.length <= segment.length*maxInterPointsDistance:
                        if prev_line == None:
                            done = True
                        else:
                            # Find vertical line
                            vert_start = new_points[-1]
                            vert_end = self.closestEnd(vert_start, goalLine)
                            vert_line = LineString([vert_start, vert_end])
                            # Calculate the angle between the new line and the vertical line
                            a_theta = self.degreeFromX(vert_line) - self.degreeFromX(new_line)
                            # Calculate the angle between the new line and the extended previous line
                            d_theta = self.degreeFromX(prev_line) - self.degreeFromX(new_line)

                            if maxAbsDegree*(-1) <= a_theta <= maxAbsDegree and maxDeltaDegree*(-1) <= d_theta <= maxDeltaDegree:
                                done = True
            
            new_points.append(new_point)
            new_start = new_point
            extend_end = new_line.interpolate(10, normalized=True)
            new_end = self.closestEnd(extend_end, goalLine)
            
            pointsOL = self.pointsOnLine(new_start, new_end, nInterPoints-(i+1))

        # final rotate to find end point is different
        final_start = new_end
        final_end = new_start
        done = False
        while not done:
            pointToRot = self.pointBetween(final_start, final_end, d=random.uniform(0, 1))
            chance = random.random()
            if chance > 0.5:
                final_rot = self.pointRotate(pointToRot, final_start, degree=90)
            else:
                final_rot = self.pointRotate(pointToRot, final_start, degree=-90)
            
            segment = LineString([final_start, final_end])
            new_line = LineString([new_points[-1], final_rot])
            prev_line = LineString([new_points[-2], new_points[-1]])
            if new_line.length <= segment.length*maxInterPointsDistance:
                # Find vertical line
                vert_start = new_points[-1]
                vert_end = self.closestEnd(vert_start, goalLine)
                vert_line = LineString([vert_start, vert_end])
                # Calculate the angle between the new line and the vertical line
                a_theta = self.degreeFromX(vert_line) - self.degreeFromX(new_line)
                # Calculate the angle between the new line and the extended previous line
                d_theta = self.degreeFromX(prev_line) - self.degreeFromX(new_line)
                if maxAbsDegree*(-1) <= a_theta <= maxAbsDegree and maxDeltaDegree*(-1) <= d_theta <= maxDeltaDegree:
                    done = True    
        
        if goalLine.contains(final_rot) == False:
            final_rot = self.closestEnd(final_rot, goalLine)
        new_points.append(final_rot)
        # 1. set intermediatePoints[] to the generated new_points[]
        self.intermediatePoints = new_points

        # 2. set nextIntermediatePointIdx to index 0
        self.nextIntermediatePointIdx = 0

        # 3. set self.finalDestination to the last item in new_points[]
        self.finalDestination = new_points[-1]




    # region 
    def degreeFromX(self, line: LineString): # TODO move to lib/Geometry
        """
        Find the angle in radian between a given line and the x-axis.
        
        Args:
            line (shapely.LineString): a line

        Returns:
            theta (float): angle in radians
        """
        # Extract points from line1 and line2
        x = line.coords[1][0] - line.coords[0][0]
        y = line.coords[1][1] - line.coords[0][1]

        # Find theta using formula
        theta = math.atan2(y, x)

        return theta

    def closestEnd(self, point: Point, goalLine: LineString):
        """
        Given a point A and a line Y, find the point B on Y such that the line AB is the shortest.

        Args:
            point (shapely.geometry.Point): point A
            goalLine (shapely.geometry.LineString): line Y

        Returns:
            end (shapely.geometry.Point): point B
        """
        d = goalLine.project(point)
        end = goalLine.interpolate(d)
        return end

    def pointBetween(self, start: Point, end: Point, d: float):
        """
        Given point A and point B, find a point C in between AB that is d distance away from A.
        
        Args:
            start (shapely.geometry.Point): point A
            end (shapely.geometry.Point): point B
            d (float): a scalar multiplier to the normalized distance between point A and point B

        Returns:
            point (shapely.geometry.Point): point C
        """
        line = LineString([start, end])
        point = line.interpolate(d, normalized=True)
        return point

    def pointRotate(self, point: Point, origin: Point, degree=90):
        """
        Given a point A and an origin O, rotate A +-90 degrees around O to get point B.

        Args:
            point (shapely.geometry.Point): point A
            origin (shapely.geometry.Point): point O
            degree (int, optional): degree of rotation. Defaults to 90

        Returns:
            rotated_point (shapely.geometry.Point): point B
        """
        rotated_point = rotate(point, degree, origin=origin)
        return rotated_point

    def pointsOnLine(self, start: Point, end: Point, n: int):
        """
        Given a start point A and an end point B, generate n number of evenly spaced points between the line AB.

        Args:
            start (shapely.geometry.Point): point A
            end (shapely.geometry.Point): point B
            n (int): number of points between the line AB

        Returns:
            pointsOL[(shapely.geometry.Point)]: the array of generated points between AB
        """
        pointsOL = [start]
        line = LineString([start, end])
        gap = 1 / (n + 1)
        d = gap
        for i in range(n):
            point = line.interpolate(d, normalized=True)
            d = d + gap
            pointsOL.append(point)
        pointsOL.append(end)
        return pointsOL
    # endregion