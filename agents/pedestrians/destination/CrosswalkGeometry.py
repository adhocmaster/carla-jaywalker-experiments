
import shapely
from shapely.geometry import LineString, Point, Polygon
import math
import random

class CrosswalkGeometry:
    # constants
    MAX_ABSOLUTE_DEGREE = math.radians(60)
    MAX_RELATIVE_DEGREE = math.radians(45)

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
        # start_x, start_y = self.source.coords[0][0], self.source.coords[0][1]
        # goalLine_x1, goalLine_y1 = self.goalLine.coords[0][0], self.goalLine.coords[0][1] 
        # goalLine_x2, goalLine_y2 = self.goalLine.coords[1][0], self.goalLine.coords[1][1]
        # # Bottom left point
        # botLeft_x = start_x - 0.5
        # botLeft_y = start_y
        # botLeft = shapely.geometry.Point((botLeft_x, botLeft_y))
        # # Bottom right point
        # botRight_x = start_x + 0.5
        # botRight_y = start_y
        # botRight = shapely.geometry.Point((botRight_x, botRight_y))
        # # Top left point
        # topLeft_x = goalLine_x1
        # topLeft_y = goalLine_y1
        # topLeft = shapely.geometry.Point((topLeft_x, topLeft_y))
        # # Top right point
        # topRight_x = goalLine_x2
        # topRight_y = goalLine_y2
        # topRight = shapely.geometry.Point((topRight_x, topRight_y))
        # # Mid left point
        # midLeft_x = min(botLeft_x, topLeft_x) + (max(botLeft_x, topLeft_x) - min(botLeft_x, topLeft_x))/1.5
        # midLeft_y = ((topLeft_y + topRight_y)/2 - botLeft_y)/2
        # midLeft = shapely.geometry.Point((midLeft_x, midLeft_y))
        # # Mid right point
        # midRight_x = min(botRight_x, topRight_x) + (max(botRight_x, topRight_x) - min(botRight_x, topRight_x))/3
        # midRight_y = ((topLeft_y + topRight_y)/2 - botRight_y)/2
        # midRight = shapely.geometry.Point((midRight_x, midRight_y))
        # # Build areaPolygon
        # areaPolygon = shapely.geometry.Polygon([botLeft, midLeft, topLeft, topRight, midRight, botRight])
        self.areaPolygon = self.genPolyArea(self.source, self.goalLine)


    def genPolyArea(self, start, goalLine):
        # Get start point coordinates
        start_x, start_y = start.coords[0][0], start.coords[0][1]
        # Extract goalLine information
        goalLine_x1, goalLine_y1 = goalLine.coords[0][0], goalLine.coords[0][1] 
        goalLine_x2, goalLine_y2 = goalLine.coords[1][0], goalLine.coords[1][1]
        
        # Bottom left point
        botLeft_x = start_x - 0.5
        botLeft_y = start_y
        botLeft = Point((botLeft_x, botLeft_y))
        # Bottom right point
        botRight_x = start_x + 0.5
        botRight_y = start_y
        botRight = Point((botRight_x, botRight_y))
        # Top left point
        topLeft_x = goalLine_x1
        topLeft_y = (goalLine_y1 + goalLine_y2) / 2
        topLeft = Point((topLeft_x, topLeft_y))
        # Top right point
        topRight_x = goalLine_x2
        topRight_y = (goalLine_y2 + goalLine_y1) / 2
        topRight = Point((topRight_x, topRight_y))
        # Mid left point
        midLeft_x = min(botLeft_x, topLeft_x) + (max(botLeft_x, topLeft_x) - min(botLeft_x, topLeft_x))/1.5
        midLeft_y = (topLeft_y - botLeft_y)/2
        print(topLeft_y, botLeft_y)
        midLeft = Point((midLeft_x, midLeft_y))
        # Mid right point
        midRight_x = min(botRight_x, topRight_x) + (max(botRight_x, topRight_x) - min(botRight_x, topRight_x))/3
        midRight_y = (topRight_y - botRight_y) / 2
        midRight = Point((midRight_x, midRight_y))
        print(midRight)

        # Build areaPolygon
        areaPolygon = Polygon([botLeft, midLeft, topLeft, topRight, midRight, botRight])
        return areaPolygon

    def generateIntermediatePoints(self, maxAbsDegree=MAX_ABSOLUTE_DEGREE, maxDeltaDegree=MAX_RELATIVE_DEGREE, nInterPoints=3, maxInterPointsDistance=1.5):
        # TODO
        # 1. find the points
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
                    segment = shapely.geometry.LineString([start, end])
                    new_line = shapely.geometry.LineString([new_points[-1], new_point])
                    prev_line = None
                    if i > 0:
                        prev_line = shapely.geometry.LineString([new_points[-2], new_points[-1]])
                    if new_line.length <= segment.length*maxInterPointsDistance:
                        if prev_line == None:
                            done = True
                        else:
                            # Find verticle line
                            vert_start = new_points[-1]
                            vert_end = self.closestEnd(vert_start, goalLine)
                            vert_line = shapely.geometry.LineString([vert_start, vert_end])
                            # Calculate the angle between the new line and the verticle line
                            a_theta = self.degreeFromX(vert_line) - self.degreeFromX(new_line)
                            # Calculate the angle between the new line and the extended previous line
                            d_theta = self.degreeFromX(prev_line) - self.degreeFromX(new_line)

                            if maxAbsDegree*(-1) <= a_theta <= maxAbsDegree and maxDeltaDegree*(-1) <= d_theta <= maxDeltaDegree:
                                # print("new line degree:", math.degrees(self.degreeFromX(new_line)))
                                # print("prev line degree:", math.degrees(self.degreeFromX(prev_line)))
                                # print("a_theta:", math.degrees(a_theta), "max:", math.degrees(maxAbsDegree))
                                # print("d_theta:", math.degrees(d_theta), "max:", math.degrees(maxDeltaDegree))
                                # print("DONE")
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
            
            segment = shapely.geometry.LineString([final_start, final_end])
            new_line = shapely.geometry.LineString([new_points[-1], final_rot])
            prev_line = shapely.geometry.LineString([new_points[-2], new_points[-1]])
            if new_line.length <= segment.length*maxInterPointsDistance:
                # Find verticle line
                vert_start = new_points[-1]
                vert_end = self.closestEnd(vert_start, goalLine)
                vert_line = shapely.geometry.LineString([vert_start, vert_end])
                # Calculate the angle between the new line and the verticle line
                a_theta = self.degreeFromX(vert_line) - self.degreeFromX(new_line)
                # Calculate the angle between the new line and the extended previous line
                d_theta = self.degreeFromX(prev_line) - self.degreeFromX(new_line)
            
                # print("check end point...")
                # print("new line degree:", math.degrees(self.degreeFromX(new_line)))
                # print("prev line degree:", math.degrees(self.degreeFromX(prev_line)))
                # print("a_theta:", math.degrees(a_theta), "max:", math.degrees(maxAbsDegree))
                # print("d_theta:", math.degrees(d_theta), "max:", math.degrees(maxDeltaDegree))
                if maxAbsDegree*(-1) <= a_theta <= maxAbsDegree and maxDeltaDegree*(-1) <= d_theta <= maxDeltaDegree:
                    done = True    
        
        if goalLine.contains(final_rot) == False:
            final_rot = self.closestEnd(final_rot, goalLine)
        new_points.append(final_rot)
        
        self.intermediatePoints = new_points

        # 2. set nextIntermediatePoint to the first one
        self.nextIntermediatePointIdx = 0

        # 3. set self.finalDestination
        self.finalDestination = new_points[-1]




    #region  ------------------------------------------------------------------------------------------------------------
    def degreeFromX(self, line: LineString): # TODO move to lib/Geometry
        """_summary_

        Args:
            line (shapely.LineString): _description_

        Returns:
            _type_: _description_
        """
        # Find the angle in radian between two given lines
        # Formula:
        # atan2(vec2.y-vec1.y, vec2.x-vec1.x)
        
        # Extract points from line1 and line2
        x = line.coords[1][0] - line.coords[0][0]
        y = line.coords[1][1] - line.coords[0][1]

        # Find theta using formula
        theta = math.atan2(y, x)

        return theta

    def closestEnd(self, point: Point, goalLine: LineString):
        """_summary_

        Args:
            point (shaply.Point): _description_
            goalLine (shapely.LineString): _description_

        Returns:
            _type_: _description_
        """
        # Given a point A and a line Y, find the point B on Y such that the line AB is the shortest
        d = goalLine.project(point)
        end = goalLine.interpolate(d)
        return end

    def pointBetween(self, start: Point, end: Point, d):
        """_summary_

        Args:
            start (shaply.Point): _description_
            end (shaply.Point): _description_
            d (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Given start point A and end point B, find a point C in between AB that is d distance away from A
        line = shapely.geometry.LineString([start, end])
        point = line.interpolate(d, normalized=True)
        return point

    def pointRotate(self, point: Point, origin: Point, degree=90):
        """_summary_

        Args:
            point (shaply.Point): _description_
            origin (shaply.Point): _description_
            degree (int, optional): _description_. Defaults to 90.

        Returns:
            _type_: _description_
        """
        # Given a point A and an origin O, rotate A +-90 degrees around O.
        rotated_point = shapely.affinity.rotate(point, degree, origin=origin)
        return rotated_point


    def pointsOnLine(self, start: Point, end: Point, n):
        """_summary_

        Args:
            start (shaply.Point): _description_
            end (shaply.Point): _description_
            n (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Given a start point A and an end point B, generate n number of evenly placed points between the line AB
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

    #endregion