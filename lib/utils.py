import carla

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
