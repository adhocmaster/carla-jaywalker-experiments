from shapely.geometry import Polygon, Point
from shapely.ops import nearest_points
from shapely.affinity import rotate, translate
import carla

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
