import carla
import math
import random
from shapely.geometry import LineString, Point

red = carla.Color(255, 0, 0)
green = carla.Color(0, 255, 0)
blue = carla.Color(47, 210, 231)
cyan = carla.Color(0, 255, 255)
yellow = carla.Color(255, 255, 0)
orange = carla.Color(255, 162, 0)
white = carla.Color(255, 255, 255)

trail_life_time = 10
waypoint_separation = 4

class Utils:

    #region simulation setup
    @staticmethod
    def createClient(logger, host, port, timeout=5.0):
        client = carla.Client(host, port)
        client.set_timeout(timeout)

        logger.info(f"Client carla version: {client.get_client_version()}")
        logger.info(f"Server carla version: {client.get_server_version()}")

        if client.get_client_version() != client.get_server_version():
            logger.warning("Client and server version mistmatch. May not work properly.")

        return client

    @staticmethod
    def getTimeDelta(world):
        settings = world.get_settings()
        return settings.fixed_delta_seconds 

    #region geometries and vector ops

    @staticmethod
    def getDirection(fromLocation, toLocation, ignoreZ=False):
        diff = toLocation - fromLocation
        if ignoreZ:
            diff.z = 0
        mag = Utils.getMagnitude(diff)
        direction =  diff / mag
        return direction

    
    @staticmethod
    def getDistance(fromLocation, toLocation, ignoreZ=False):
        diff = toLocation - fromLocation
        if ignoreZ:
            diff.z = 0
        
        return Utils.getMagnitude(diff)

        
    @staticmethod
    def getMagnitude(vector: carla.Vector3D):
        return math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)


    @staticmethod
    def multiplyNumber(vector: carla.Vector3D, number):
        return carla.Vector3D(
            x=vector.x * number,
            y=vector.y * number,
            z=vector.z * number
        )

    @staticmethod
    def createRandomVector(min, max) -> carla.Vector3D:
        return carla.Vector3D(
            x=random.uniform(min, max),
            y=random.uniform(min, max),
            z=random.uniform(min, max)
        )


    
    @staticmethod
    def getLineSegment(vel1: carla.Vector3D, start1: carla.Location, seconds=10):
        end1 = start1 + vel1 * seconds
        lineS1 = LineString([
            (start1.x, start1.y),
            (end1.x, end1.y)
        ])

        return lineS1


    @staticmethod
    def getConflictPoint(vel1: carla.Vector3D, start1: carla.Location, vel2: carla.Vector3D, start2: carla.Location, seconds=10) -> carla.Location:
        """returns if there is a conflict, but not necessarily they will collide with each other, 

        Args:
            vel1 (carla.Vector3D): [description]
            start1 (carla.Location): head location of actor 1
            vel2 (carla.Vector3D): [description]
            start2 (carla.Location): head location of actor 2
            seconds (int, optional): [description]. Defaults to 10.

        Returns:
            [type]: [description]
        """

        end1 = start1 + vel1 * seconds
        end2 = start2 + vel2 * seconds

        lineS1 = Utils.getLineSegment(vel1, start1, seconds)
        lineS2 = Utils.getLineSegment(vel2, start2, seconds)

        point = lineS1.intersection(lineS2)

        if isinstance(point, Point):
            return carla.Location(x = point.x, y = point.y, z=0)
            # return point
        
        return None

    @staticmethod
    def getCollisionPointAndTTC(vel1: carla.Vector3D, start1: carla.Location, vel2: carla.Vector3D, start2: carla.Location, seconds=10):

        """vehicle, and, walker has bounding_box relative to their actor center
        """
        
        # bbActor1.logger.info("Actor 1 BB center {bbActor1.bounding_box.location}")
        # bbActor2.logger.info("Actor 2 BB center {bbActor2.bounding_box.location}")
        
        # bb1 = carla.BoundingBox(
        #     extent = bbActor1.extent,
        #     location = bbActor1.bounding_box.location + bbActor1.get_location(),
        #     rotation = bbActor1.bounding_box.rotation + bbActor1.get_transform().rotation
        # )
        # bb2 = carla.BoundingBox(
        #     extent = bbActor2.extent,
        #     location = bbActor2.bounding_box.location + bbActor1.get_location(),
        #     rotation = bbActor2.bounding_box.rotation + bbActor2.get_transform().rotation
        # )
        # bbActor1.logger.info("BB center {bb1.location}")
        # bbActor2.logger.info("BB center {bb2.location}")


        # Find conflict point. In some rare cases it will give us no conflict, but there will still be a conflict.
        conflictPoint = Utils.getConflictPoint(
            vel1 = vel1,
            start1 = start1,
            vel2 = vel2,
            start2 = start2,
            seconds=seconds)

        # If no conflict point, disregard? 

        if conflictPoint is None:
            return None, None

        # time to conflict point
        distance1 = start1.distance_2d(conflictPoint)
        delta1 = distance1 / vel1.length()

        distance2 = start2.distance_2d(conflictPoint)
        delta2 = distance2 / vel2.length()


        if abs(delta1 - delta2) < 1: # we assume they will collide with each other.
            TTC = min(delta1, delta2)
            return conflictPoint, TTC
        
        return None, None


        # location of 2, after that time


        # check bounding box overlaps with 


    @staticmethod
    def getMaxExtent(bbActor):
        extent = math.sqrt( bbActor.bounding_box.extent.x ** 2 + bbActor.bounding_box.extent.y ** 2)
        return extent


    #endregion

    #region drawing
    @staticmethod
    def draw_transform(debug, trans, col=carla.Color(255, 0, 0), lt=-1):
        debug.draw_arrow(
            trans.location, trans.location + trans.get_forward_vector(),
            thickness=0.05, arrow_size=0.1, color=col, life_time=lt)


    @staticmethod
    def draw_waypoint_union(debug, w0, w1, color=carla.Color(255, 0, 0), lt=5):
        debug.draw_line(
            w0.transform.location + carla.Location(z=0.25),
            w1.transform.location + carla.Location(z=0.25),
            thickness=0.1, color=color, life_time=lt, persistent_lines=False)
        debug.draw_point(w1.transform.location + carla.Location(z=0.25), 0.1, color, lt, False)
    
    @staticmethod
    def draw_waypoints(debug, waypoints, z=0.5, color=(255,0,0), life_time=1.0):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        for wpt in waypoints:
            wpt_t = wpt.transform
            begin = wpt_t.location + carla.Location(z=z)
            angle = math.radians(wpt_t.rotation.yaw)
            end = begin + carla.Location(x=math.cos(angle), y=math.sin(angle))
            debug.draw_arrow(begin, end, arrow_size=0.3, color=carla.Color(*color), life_time=life_time)

    @staticmethod
    def draw_trace_route(debug, route, color=(150, 150, 0), life_time=10):
        
        print(f"length of trace route {len(route)}")
        wps = []
        for (wp, ro) in route:
            wps.append(wp)
        
        Utils.draw_waypoints(debug, wps, color=color, life_time=life_time)

    @staticmethod
    def log_route(logger, route):
        for (wp, ro) in route:
            logger.info(wp.transform.location)
        


    @staticmethod
    def draw_waypoint_info(debug, w, lt=5):
        w_loc = w.transform.location
        debug.draw_string(w_loc + carla.Location(z=0.5), "lane: " + str(w.lane_id), False, yellow, lt)
        debug.draw_string(w_loc + carla.Location(z=1.0), "road: " + str(w.road_id), False, blue, lt)
        debug.draw_string(w_loc + carla.Location(z=-.5), str(w.lane_change), False, red, lt)

    @staticmethod
    def draw_junction(debug, junction, l_time=10):
        """Draws a junction bounding box and the initial and final waypoint of every lane."""
        # draw bounding box
        box = junction.bounding_box
        point1 = box.location + carla.Location(x=box.extent.x, y=box.extent.y, z=2)
        point2 = box.location + carla.Location(x=-box.extent.x, y=box.extent.y, z=2)
        point3 = box.location + carla.Location(x=-box.extent.x, y=-box.extent.y, z=2)
        point4 = box.location + carla.Location(x=box.extent.x, y=-box.extent.y, z=2)
        debug.draw_line(
            point1, point2,
            thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
        debug.draw_line(
            point2, point3,
            thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
        debug.draw_line(
            point3, point4,
            thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
        debug.draw_line(
            point4, point1,
            thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
        # draw junction pairs (begin-end) of every lane
        junction_w = junction.get_waypoints(carla.LaneType.Any)
        for pair_w in junction_w:
            Utils.draw_transform(debug, pair_w[0].transform, orange, l_time)
            debug.draw_point(
                pair_w[0].transform.location + carla.Location(z=0.75), 0.1, orange, l_time, False)
            Utils.draw_transform(debug, pair_w[1].transform, orange, l_time)
            debug.draw_point(
                pair_w[1].transform.location + carla.Location(z=0.75), 0.1, orange, l_time, False)
            debug.draw_line(
                pair_w[0].transform.location + carla.Location(z=0.75),
                pair_w[1].transform.location + carla.Location(z=0.75), 0.1, white, l_time, False)
    #endregion