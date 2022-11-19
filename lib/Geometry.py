import carla
import copy
import math
from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import scale, rotate
from typing import List, Tuple

class Geometry: 

    visualizer = None


    @staticmethod
    def getGlobalYaw(subject: carla.Vector3D): 
        """Returns rotation around Z"""
        return math.atan2(subject.y, subject.x)

    
    @staticmethod
    def changeCartesianCenter(subject: carla.Vector3D, center: carla.Vector3D, centerDirection: carla.Vector3D=None, centerRotation=None) -> carla.Vector3D:

        clone = subject - center 
        # clone = carla.Vector3D(x=subject.x, y=subject.y, z=subject.z)
        # clone.x -= center.x
        # clone.y -= center.y
        # clone.z -= center.z

        if centerDirection is not None:
            angle = -Geometry.getGlobalYaw(centerDirection)
            clone = Geometry.rotateAroundZ(clone, angle)
        elif centerRotation is not None:
            angle = -centerRotation
            clone = Geometry.rotateAroundZ(clone, angle)


        return clone
    

    @staticmethod
    def rotateAroundZ(subject: carla.Vector3D, angle) -> carla.Vector3D:
        """_summary_

        Args:
            subject (carla.Vector3D): _description_
            angle (_type_): If we are transforming to another reference frame, angle should negated 

        Returns:
            carla.Vector3D: _description_
        """

        clone = carla.Vector3D(x=subject.x, y=subject.y, z=subject.z)
        clone.x = subject.x * math.cos(angle) - subject.y * math.sin(angle)
        clone.y = subject.x * math.sin(angle) + subject.y * math.cos(angle)
        
        return clone

    
    @staticmethod
    def distanceTuples(point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    @staticmethod
    def locationToPoint(location: carla.Location) -> Point:
        return Point(location.x, location.y)
    
    @staticmethod 
    def pointtoLocation(point: Point) -> carla.Location:
        return carla.Location(point[0], point[1], 0.1)


    #region scanning for sidewalks


    @staticmethod
    def makeCenterScanLine(source: carla.Location, dest: carla.Location, scaleFactor:float = 1.5) -> LineString:

        s = (source.x, source.y)
        d = (dest.x, dest.y)
        yAxis = LineString([s, d])
        centerScanLine = scale(yAxis, xfact=scaleFactor, yfact=scaleFactor, origin=s)
        return centerScanLine


    @staticmethod
    def findClosestSidewalkLocationToDirection(
            world:carla.World, 
            source: carla.Location, 
            direction: carla.Vector3D,
            scanRadius = 20
        ) -> carla.Location:
        """Given a source point on a road this method returns the closest point on the sidewalk on the other side of the road. 

        Args:
            source (carla.Location): any point on the road
            direction (carla.Vector3D): direction to search, useful when the current sidewalk (or island) is in the middle of the road.
            scanRadius (float): maximum scan radius for ray tracing for sidwalks. Defaults to 20 meters.

        Returns:
            carla.Location: a point on another sidewalk, or None if not sidewalk on the other side of the road.
        """

        # if direction is not None:
            

        sidewalkPoint, centerLine = Geometry.getClosestSidewalkPointAndScanLine(
            world=world,
            source=source,
            direction=direction,
            scanRadius=scanRadius
        )

        return Geometry.pointtoLocation(sidewalkPoint)


    @staticmethod
    def findClosestSidewalkLocationOnTheOtherSide(
            world:carla.World, 
            source: carla.Location, 
            scanRadius = 20
        ) -> carla.Location:
        """Given a source point on a sidewalk, this method returns the closest point on the sidewalk on the other side of the road. 

        Args:
            source (carla.Location): source is a point on the current sidewalk. If the point is not on a sidewalk, provide a direction to search in.
            scanRadius (float): maximum scan radius for ray tracing for sidwalks. Defaults to 20 meters.

        Returns:
            carla.Location: a point on another sidewalk, or None if not sidewalk on the other side of the road.
        """

        # if direction is not None:
            

        sidewalkPoint, centerLine = Geometry.getClosestSidewalkPointAndScanLine(
            world=world,
            source=source,
            direction=None,
            scanRadius=scanRadius
        )

        return Geometry.pointtoLocation(sidewalkPoint)

    @staticmethod
    def getClosestSidewalkPointAndScanLine(
            world:carla.World, 
            source: carla.Location, 
            direction: carla.Vector3D = None,
            scanRadius = 20,
            fov:float = 90,
            ignoreLessThan=4.0
            ) -> LineString:
        """_summary_

        Args:
            world (carla.World): _description_
            source (carla.Location): a point on a sidewalk if direction is None. A point on the road if a direction is given.
            direction (carla.Vector3D, optional): Limit search towards a direction. Defaults to None.
            scanRadius (float): maximum scan radius for ray tracing for sidwalks. Defaults to 20 meters.
            fov (float, optional): Limit search inside a fov. Defaults to 90.
            ignoreLessThan (float, optional): _description_. Defaults to 4.0.

        Returns:
            LineString: _description_
        """

        curMin = 60
        centerScanLine = None

        # broad scan in 360
        if direction is None:
            scanLines = Geometry.get360ScanLines(source, 10, scanRadius)

            if Geometry.visualizer is not None:
                for scanLine in scanLines:
                    Geometry.visualizer.drawShapelyLine(scanLine, life_time=3)

            for scanLine in scanLines:
                sidewalkPoint = Geometry.getSideWalkPointOnScanLine(world, scanLine)
                if sidewalkPoint is None:
                    continue
                sidewalkLocation = Geometry.pointtoLocation(sidewalkPoint)
                d = source.distance_2d(sidewalkLocation)
                # print("d", d)
                if d > ignoreLessThan and d < curMin:
                    curMin = d
                    centerScanLine = scanLine
        else:
            targetLocation = direction * scanRadius + source
            centerScanLine = Geometry.makeCenterScanLine(source, targetLocation)
            
        # narrow scan

        assert centerScanLine is not None
        
        if Geometry.visualizer is not None:
            Geometry.visualizer.drawShapelyLine(centerScanLine, color=(0, 0, 255, 100), life_time=3)

        return Geometry.getClosestSidewalkPointAndLineAroundAScanLine(
            world=world,
            centerScanLine=centerScanLine,
            nLines=10,
            fov=fov
        )


    @staticmethod
    def getClosestSidewalkPointAndLineAroundAScanLine(
            world:carla.World, 
            centerScanLine: LineString,
            nLines=20,
            fov=90,
            ignoreLessThan=4.0
        ):
    
        narrowScanLines, sidewalkPoints = Geometry.getScanLinesAndSidewalkPoints(
            world=world,
            centerScanLine=centerScanLine,
            nLines=10,
            fov=fov
        )

        source = Geometry.pointtoLocation(centerScanLine.coords[0])

        if Geometry.visualizer is not None:
            for scanLine in narrowScanLines:
                Geometry.visualizer.drawShapelyLine(scanLine, life_time=3)

        curMin = 60
        minSidewalkPoint = None
        for sidewalkPoint in sidewalkPoints:
            sidewalkLocation = Geometry.pointtoLocation(sidewalkPoint)
            d = source.distance_2d(sidewalkLocation)
            if d > ignoreLessThan and d < curMin:
                curMin = d
                centerScanLine = scanLine
                minSidewalkPoint = sidewalkPoint


        return minSidewalkPoint, centerScanLine

    @staticmethod
    def get360ScanLines(source: carla.Location, nLines = 10, scanRadius = 20) -> List[LineString]:

        stepAngle = 360 // nLines

        # a randomLine
        aRandomEndPoint = carla.Location(source.x + scanRadius, source.y, source.z)
        firstLine = Geometry.makeCenterScanLine(
            source=source,
            dest=aRandomEndPoint,
            scaleFactor=1.0
            )

        lines = [firstLine]
        for i in range(1, nLines+1):
            angle = stepAngle * i
            lines.append(rotate(firstLine, angle, origin=firstLine.coords[0]))
        
        return lines



    @staticmethod
    def getSideWalkPointOnScanLine(world:carla.World, scanLine: LineString) -> Point:
        """gets a point on the sidewalk 1 meter inside from the edge of detection, ray is casted from the first coord towards the last coord of the line.

        Args:
            world (carla.World): _description_
            scanLine (LineString): _description_

        Returns:
            Point: _description_
        """
        
        initialLocaltion = carla.Location(scanLine.coords[0][0], scanLine.coords[0][1], 0.1)
        endLocation = carla.Location(scanLine.coords[1][0], scanLine.coords[1][1], 0.1)
        objectsInPath = world.cast_ray(initialLocaltion, endLocation)
        for obj in objectsInPath:
            # print(f"type: {obj.label}, position: {obj.location}")
            if obj.label == carla.CityObjectLabel.Sidewalks:
                sideWalkLine = LineString([scanLine.coords[0], (obj.location.x, obj.location.y)])
                scaleFactor = (sideWalkLine.length + 1) / sideWalkLine.length
                sideWalkLine = scale(sideWalkLine, xfact=scaleFactor, yfact=scaleFactor, origin=scanLine.coords[0])
                return sideWalkLine.coords[1]
        
        return None


    @staticmethod
    def getScanLinesAndSidewalkPoints(
            world:carla.World, 
            centerScanLine: LineString,
            nLines:int = 20,
            fov:float = 120
        ) -> Tuple[List[LineString], List[Point]]:
        
        """Sequentially searches for sidewalk from the center scan line. whenever it cannot detect a sidewalk, the search stops.

        Args:
            centerScanLine (LineString): line between the origin and the ideal destination
            nLines (int): number of points
            fov (float): field of view in degrees

        Returns:
            _type_: _description_
        """
        
        angleStep = fov / nLines

        rightScanLines = []
        rightSideWalkPoints = []
        for i in range(1, nLines // 2):
            angle = angleStep * i
            newLine = rotate(centerScanLine, angle, origin=centerScanLine.coords[0])
            sideWalkPoint = Geometry.getSideWalkPointOnScanLine(world, newLine)
            if sideWalkPoint is not None:
                rightScanLines.append(newLine)
                rightSideWalkPoints.append(sideWalkPoint)
            else:
                break
        
        
        leftScanLines = []
        leftSideWalkPoints = []
        for i in range(1, nLines // 2):
            angle = -angleStep * i
            newLine = rotate(centerScanLine, angle, origin=centerScanLine.coords[0])
            sideWalkPoint = Geometry.getSideWalkPointOnScanLine(world, newLine)
            if sideWalkPoint is not None:
                leftScanLines.append(newLine)
                leftSideWalkPoints.append(sideWalkPoint)
            else:
                break
        
        leftScanLines.reverse()
        leftSideWalkPoints.reverse()

        return leftScanLines + rightScanLines, leftSideWalkPoints + rightSideWalkPoints

    #endregion


    
