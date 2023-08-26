import math
from shapely.geometry import Polygon, Point
from shapely.ops import nearest_points
from shapely.affinity import rotate, translate
import carla

from lib.utils import Utils

class VehicleUtils:

    @staticmethod
    def getYANGContour(vehicle: carla.Vehicle) -> Polygon:

        # constants
        alphaX = 1.394358
        dKnotX = 0.510985
        le = 0.2151011

        bb = vehicle.bounding_box

        # reactangle length + 2le + dKnotX, width + 2le

        length = bb.extent.x * 2 + 2 * le + dKnotX
        width = bb.extent.y * 2 + 2 * le

        longitudinalSpeed = vehicle.get_velocity().length() # TODO, get the longitudinal component only. which is the projection on the waypoint direction.

        headLength = alphaX * longitudinalSpeed

        # print(bb.extent.x, bb.extent.y)
        # print(le, dKnotX, headLength)
        localVertices = [
            (-(bb.extent.x + le), bb.extent.y), # top left,
            (bb.extent.x + le + dKnotX, bb.extent.y), # top right,
            ((bb.extent.x + le + dKnotX + headLength), 0), # head,
            ((bb.extent.x + le + dKnotX), -bb.extent.y), # bot right,
            (-(bb.extent.x + le), -bb.extent.y) # bot left,

        ]

        localCenter = vehicle.get_location()
        localRotation = vehicle.get_transform().rotation.yaw

        localContour = Polygon(localVertices)

        translatedContour = translate(localContour, xoff=localCenter.x, yoff=localCenter.y)
        globalContour = rotate(translatedContour, localRotation)

        # print("localVertices", localVertices)
        # print("localCenter", localCenter)
        # print("localRotation", localRotation)

        # print(localContour.exterior.xy)
        # print(translatedContour.exterior.xy)
        # print(globalContour.exterior.xy)

        return globalContour

        # head point: alphaX * longitudinalSpeed

        # transform points from vehicle center to world coordinates

    @staticmethod
    def getNearestPointOnYANGVehicleContour(vehicle: carla.Vehicle, source: carla.Location) -> carla.Location:
        contour = VehicleUtils.getYANGContour(vehicle)
        points = nearest_points(contour, Point(source.x, source.y))
        return carla.Location(x=points[0].x, y=points[0].y)
    
    # @staticmethod
    # def getVehicleLocation(vehicle: carla.Vehicle, source: carla.Location) -> carla.Location:
    #     nearestPointOnVehicle = VehicleUtils.getNearestPointOnYANGVehicleContour(vehicle, source)
    #     return nearestPointOnVehicle

    @staticmethod
    def getVehicleFrontLocation(vehicle: carla.Vehicle) -> carla.Location:
        bb = vehicle.bounding_box
        localFront = carla.Location(x=bb.extent.x, y=0, z=0)
        globalFront = vehicle.get_transform().transform(localFront)
        return globalFront
    
    @staticmethod
    def getVehicleBackLocation(vehicle: carla.Vehicle) -> carla.Location:
        bb = vehicle.bounding_box
        localFront = carla.Location(x=-bb.extent.x, y=0, z=0)
        globalFront = vehicle.get_transform().transform(localFront)
        return globalFront
    
    def getNearestLocationOnVehicleAxis(fromLocation: carla.Location, vehicle: carla.Vehicle, vehicleWp: carla.Waypoint) -> carla.Location:
        """Gets the front or back location of the vehicle

        Args:
            fromLocation (carla.Location): _description_
            vehicle (carla.Vehicle): _description_
            vehicleWp (carla.Waypoint): _description_

        Returns:
            carla.Location: _description_
        """
        
        if VehicleUtils.isVehicleBehindLocation(fromLocation, vehicle, vehicleWp):
            vehicleLocation = VehicleUtils.getVehicleFrontLocation(vehicle)
            print("vehicle is behind the location")
        else:
            vehicleLocation = VehicleUtils.getVehicleBackLocation(vehicle)
            print("vehicle is in front of the location")

        return vehicleLocation
    
    
    def isVehicleBehindLocation(fromLoc: carla.Location, vehicle: carla.Vehicle, vehicleWp: carla.Waypoint) -> bool:
        """Checks if the vehicle is behind the location

        Args:
            fromLoc (carla.Location): _description_
            vehicle (carla.Vehicle): _description_

        Returns:
            bool: _description_
        """
        vehicleDirection = vehicleWp.transform.get_forward_vector()
        vehicleToNavLoc = fromLoc - vehicle.get_location() # todo add front location to check
        # vehicleToNavLoc = fromLoc - vehicle.get_location()
        angle = abs(Utils.angleBetweenVectors(vehicleDirection, vehicleToNavLoc))
        # print("angle", math.degrees(angle))
        if angle >= math.pi / 2:
            return False
        return True

    @staticmethod 
    def distanceToVehicle(fromLocation: carla.Location, vehicle: carla.Vehicle, vehicleWp: carla.Waypoint):

        vehicleLocation = VehicleUtils.getNearestLocationOnVehicleAxis(fromLocation, vehicle, vehicleWp)
        print("fromLocation", fromLocation)
        print("vehicle original location", vehicle.get_location())
        print("vehicle nearest", vehicleLocation)
        print("bounding box extent", vehicle.bounding_box.extent)
        print(f"Distance to vehicle {fromLocation.distance_2d(vehicleLocation)}")
        # print(f"vehicle bbox x {vehicle.bounding_box.extent.x}")

        # return fromLocation.distance_2d(vehicle.bounding_box.location) - vehicle.bounding_box.extent.x
        return fromLocation.distance_2d(vehicleLocation)
