import carla
import numpy as np
import random
import math
from shapely.geometry import LineString, Point, Polygon

from .LoggerFactory import LoggerFactory
from .ClientUser import ClientUser
from .MapManager import MapManager
from typing import Dict, List, Union
# import agents.pedestrians.PedState as PedState

class SimulationVisualization(ClientUser):

    def __init__(self, client: carla.Client, mapManager: MapManager):
        self.name = "SimulationVisualization"
        super().__init__(client)

        self.logger = LoggerFactory.create(self.name)

        self.mapManager = mapManager
        # self.pool = eventlet.GreenPool()

        self.tracking = {} # actor id -> tracking config

        self.trackingAgent = {} # agent actor id -> agent
        # self.pool.spawn_n(self.world.on_tick, self.onTick)
        # self.world.on_tick(self.onTick) # freezes. may need greenlets.

    

    def trackAgentOnTick(self, agent):
        if agent is None:
            return
        self.trackingAgent[agent.vehicle.id] = agent


    # def onTick(self, world_snapshot):
    #     for actorId in self.tracking:
    #         actor_snapshot = world_snapshot.find(actorId)
    #         if actor_snapshot is not None:
    #             life_time = self.tracking[actorId]["life_time"]
    #             color = self.tracking[actorId]["color"]
    #             self.drawWalkerBB(actor_snapshot, color=color, life_time=life_time)

    def onTick(self, world_snapshot):
        for agent in self.trackingAgent.values():
            self.drawAgentStatus(agent)


    #region unit functions

    def getRandomColor(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(0, 100)

        return (r, g, b, a)

    
    def drawPoint(self, location, size=0.1, color=(255,0,0,100), life_time = 0):
        self.debug.draw_point(location, size, carla.Color(*color),  life_time)
    
    def drawShaplyPoint(self, point: Point, size=0.1, color=(255,0,0,100), life_time = 0, z=0.5):
        location = carla.Location(point[0], point[1], z)
        self.drawPoint(location, size, color, life_time)

    def drawShaplyPolygon(self, polygon: Polygon, size=0.1, color=(255,0,0,100), life_time = 0, z=0.5):
        X = polygon.exterior.xy[0]
        Y = polygon.exterior.xy[1]
        for point in zip(X, Y):
            self.drawShaplyPoint(point, size, color, life_time, z=z)
    
    def drawPoints(self, locations:List[carla.Location], size=0.1, color=(255,0,0,100), life_time = 0):
        for location in locations:
            self.drawPoint(location, size, color, life_time) 


    def drawLine(self, begin, end, thickness=0.1, color=(255,0,0,100), life_time = 1.0):
        self.debug.draw_line(begin, end, thickness, carla.Color(*color), life_time)

    def drawShapelyLine(self, line: LineString, thickness=0.1, color=(255,0,0,100), life_time = 1.0):
        a = carla.Location(line.coords[0][0], line.coords[0][1], 0.5)
        b = carla.Location(line.coords[1][0], line.coords[1][1], 0.5)
        self.drawLine(a, b, thickness, color, life_time)

    def drawBox(self, bb, rotation = carla.Rotation(), thickness=0.1, color=(255,0,0, 100), life_time = 0):
        self.debug.draw_box(
                    bb,
                    rotation, 
                    thickness, 
                    carla.Color(*color),
                    life_time)

    def drawTextOnMap(self, location, text, color=(0, 0, 0), life_time=600):
        self.drawText(
            location=location, 
            text=text, 
            draw_shadow = True,
            color=color,
            life_time=life_time
        )

    def drawText(self, location, text, draw_shadow=False, color=(255,0,0), life_time=600):
        """[summary]

        Args:
            location ([type]): [description]
            text ([type]): [description]
            draw_shadow (bool, optional): [description]. Defaults to False.
            color (tuple, optional): [description]. Defaults to (255,0,0).
            life_time (float, optional): [description]. > 1. 0 or -1 has no effect.
        """
        self.debug.draw_string(
            location, 
            text, 
            draw_shadow,
            carla.Color(*color),
            life_time
            )

        # self.debug.draw_string(
        #     location, 
        #     "Where is my text", 
        #     False,
        #     carla.Color(0, 0, 0, 0),
        #     life_time
        #     )


    def drawShapelyPolygon(self, polygon: Polygon, thickness=0.1, color=(255,0,0,100), life_time = 1.0):
        prevPoint = polygon.exterior.coords[0]
        for nextPoint in polygon.exterior.coords[1:]:
            line = LineString([prevPoint, nextPoint])
            self.drawShapelyLine(line, thickness, color, life_time)
            prevPoint = nextPoint
    
    
    def draw00(self):
        bb = carla.BoundingBox(
            carla.Location(x=0, y=0, z=0), 
            carla.Vector3D(1,1,1) # assuming all walkers are less than 2 meters in height
        )
        rotation = carla.Rotation(pitch=-90)
        self.drawBox(bb, rotation, thickness=0.1, color=(0, 0, 0, 0))

    def drawWalkerBB(self, walker, thickness=0.1, color=(255,0,0, 100), life_time = 0):
        bb = self.getWalkerBB(walker)
        rotation = walker.get_transform().rotation
        self.drawBox(bb, rotation, thickness=thickness, color=color, life_time=life_time)

    def getWalkerBB(self, walker):
        return carla.BoundingBox(
            walker.get_transform().location, 
            carla.Vector3D(0.5,0.5,2) # assuming all walkers are less than 2 meters in height
        )

    # trajectory

    def trackOnTick(self, actorId, config=None):
        if config is None:
            config = { 'life_time': 0 }

        if 'color' not in config:
            config['color'] = self.getRandomColor()

        self.tracking[actorId] = config
    

    # some positional information

    def drawWalkerNavigationPoints(self, navPoints: Union[List[carla.Transform], List[carla.Location]], size=0.05, z=0.5, color=(0, 255, 0), coords=True, life_time=10.0):
        for point in navPoints:
            location = point
            if isinstance(point, carla.Transform):
                location = point.location
            location.z = z
            self.logger.debug(f"walker spawn position ({location.x}, {location.y})")
            self.drawPoint(location=location, size=size, color=color, life_time=life_time)
            if coords:
                self.drawTextOnMap(location=carla.Location(location.x, location.y, 1), text=f"({round(location.x)}, {round(location.y)})", life_time=life_time)

    def drawSpawnPoints(self, dropout=0.5, life_time=0.0):
        """
        Arguments:
            dropout : probability that a point will be drawn on the map.
        """
        spawn_points = self.map.get_spawn_points()
        for point in spawn_points:
            if random.uniform(0,1) > dropout:
                location = point.location
                self.logger.debug(f"spawn_point position ({location.x}, {location.y})")
                self.drawPoint(location=location, size=0.05, life_time=life_time)
                self.drawTextOnMap(location=carla.Location(location.x, location.y, 1), text=f"({round(location.x)}, {round(location.y)})", life_time=life_time)


    def drawSpectatorPoint(self):
        spectator = self.world.get_spectator()
        location = spectator.get_location()
        self.logger.debug(f"spectator position ({location.x}, {location.y}, {location.z})")
        drawLocation = carla.Location(location.x, location.y, 0)
        self.drawPoint(location=drawLocation, size=0.1, color=(0, 50, 200))
        self.drawTextOnMap(location=carla.Location(location.x, location.y, 10), text=f"Center ({round(location.x)}, {round(location.y)})")

        

    def drawAllWaypoints(self, z=0.5, life_time=1.0, position=False):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        self.drawWaypoints(self.mapManager.waypoints, life_time=life_time, position=position)

    def drawWaypoints(self, waypoints, color=(10,10,10, 50), z=0.1, life_time=1.0, position=False, yaw=False):
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
            self.world.debug.draw_arrow(
                begin, 
                end, 
                thickness=0.05,
                arrow_size=0.2, 
                color=carla.Color(*color), 
                life_time=life_time
                )
            
            if position:
                textLoc = carla.Location(wpt_t.location.x, wpt_t.location.y, 0.5)
                # if wpt_t.rotation.yaw > 0:
                #     # textLoc.x += 3
                #     textLoc.y -= 12
                # print(textLoc)
                if yaw:
                    self.drawTextOnMap(location=textLoc, text=f"({wpt_t.location.x:.1f}, {wpt_t.location.y:.1f}, {wpt_t.rotation.yaw:.1f})")
                else:
                    self.drawTextOnMap(location=textLoc, text=f"({wpt_t.location.x:.1f}, {wpt_t.location.y:.1f})")

                
    def drawTraceRoute(self, route, color=(50, 50, 0), life_time=10):
        
        # print(f"Utils->draw_trace_route: length of trace route {len(route)}")
        wps = []
        for (wp, ro) in route:
            wps.append(wp)
        
        self.drawWaypoints(wps, color=color, life_time=life_time)



    def drawDirection(self, location, direction, z=0.5, life_time=1.0):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        begin = location + carla.Location(z=z)
        angle = math.atan2(direction.y, direction.x)
        end = begin + carla.Location(x=math.cos(angle), y=math.sin(angle))
        self.world.debug.draw_arrow(
            begin, 
            end, 
            arrow_size=0.3, 
            color=carla.Color(50, 25, 25), 
            life_time=life_time
            )


    def drawForce(self, location, force:carla.Vector3D, color=(50, 25, 25), z=0.5, life_time=1.0):
        """
        Draw a list of waypoints at a certain height given in z.

            :param world: carla.world object
            :param waypoints: list or iterable container with the waypoints to draw
            :param z: height in meters
        """
        begin = location + carla.Location(z=z)
        if force.length() < 0.001:
            return
        direction = force.make_unit_vector()
        magnitude = force.length()
        angle = math.atan2(direction.y, direction.x)
        end = begin + carla.Location(
                                        x=math.cos(angle) * magnitude, 
                                        y=math.sin(angle) * magnitude
                                    )

        self.world.debug.draw_arrow(
            begin, 
            end, 
            arrow_size=0.3, 
            color=carla.Color(*color), 
            life_time=life_time
            )



    def drawDestinationPoint(self, location, color=(0, 255, 0), life_time=20.0):
        self.logger.debug(f"destinationSpawnPoint position ({location.x}, {location.y})")
        overlayLocation = carla.Location(location.x, location.y, 0.5)
        self.drawPoint(location=overlayLocation, size=0.2, color=color, life_time=life_time)
        self.drawTextOnMap(location=overlayLocation - carla.Location(x=-.6, y=.5), text=f"D ({location.x},{location.y})", color=(10, 10, 10, 255), life_time=life_time/2)

    
    def drawPedState(self, state, walker, life_time=0.1, location=None):

        from agents.pedestrians.PedState import PedState
        color = (0, 0, 0)
        if state == PedState.CROSSING:
            color = (0, 150, 50)
        if state == PedState.WAITING:
            color = (200, 180, 0)
        if state == PedState.FROZEN:
            color = (255, 0, 0)

        # self.drawWalkerBB(walker, color = color, life_time=0.1)
        if location is not None:
            overlayLocation = location
        else:
            overlayLocation = walker.get_location() + carla.Location(z=1)

        self.drawTextOnMap(location=overlayLocation, text=state.value, color=color, life_time=life_time)

    

    def visualizeForces(self, title, forces:Dict[str, carla.Vector3D], forceCenter: carla.Location, infoCenter: carla.Location, life_time=0.1):
        """[summary]

        Args:
            forces (dict): name -> vector3D
        """
        # draw names
        # in our case change x values
        x = infoCenter.x
        y = infoCenter.y
        # z = infoCenter.z
        z = 1
        overlayLocation = carla.Location(
                x = x,
                y = y,
                z = z
            )

        self.drawTextOnMap(location=overlayLocation, text=title, life_time=life_time)
        offsetX = 1
        offsetY = 0
        colors = self._getForceColors()
        for name in forces:
            color = colors.pop(0)
            x = x + offsetX
            y = y + offsetY
            nameLocation = carla.Location(
                x = x,
                y = y,
                z = z
            )
            force = forces[name]
            if force is None:
                length = 0
            else:
                length = force.length()

            # print(f"{name} force = {length} at {nameLocation}")

            self.drawTextOnMap(location=nameLocation, text=f"{name} force = {length}", color=color, life_time=life_time)
            if force is not None and force.length() > 0:
                self.drawForce(forceCenter, force, color=color, life_time=life_time)

    
    def _getForceColors(self):
        pallete = [
            (0, 100, 0),
            (100, 0, 0),
            (0, 0, 100),
            (50, 100, 0),
            (0, 100, 50),
            (100, 50, 0),
            (100, 0, 50),
            (0, 50, 100),
            (50, 0, 100)
            
        ]
        return pallete

    def drawAgentStatus(self, vehicleAgent):
        self.draw_target_waypoint(vehicleAgent)
        self.draw_global_plan(vehicleAgent)
        # self.draw_steering_direction(vehicleAgent)
        pass

    def draw_target_waypoint(self, agent):
        target_waypoint = agent.motor_control.target_waypoint
        if target_waypoint is not None:
            self.drawWaypoints([target_waypoint],
                                color=(255, 0, 0),
                                z=1.5,
                                life_time=1)
    
    def draw_global_plan(self, vehicleAgent):
        globalPlan = vehicleAgent.local_map.global_plan
        waypoints = []
        for wp, _ in globalPlan:
            waypoints.append(wp)
        self.drawWaypoints(waypoints, color=(0, 255, 0), life_time=1)
        pass


    def draw_steering_direction(self, vehicleAgent, line_size=5.0):

        vehicle_location = vehicleAgent.vehicle.get_location()
        vehicle_location = carla.Location(x=vehicle_location.x, y=vehicle_location.y, z=1.5)
        vehicle_forward_vector = vehicleAgent.vehicle.get_transform().get_forward_vector()

        control = vehicleAgent.get_vehicle_control()
        steering_angle = control.steer


        vehicle_forward_vector3D = carla.Vector3D(vehicle_forward_vector.x, vehicle_forward_vector.y, 0)
        vehicle_forward_vector_end_point = vehicle_location + carla.Vector3D(vehicle_forward_vector3D.x * line_size, vehicle_forward_vector3D.y * line_size, 0)

        steering_vector_x = vehicle_forward_vector3D.x * math.cos(steering_angle) - vehicle_forward_vector3D.y * math.sin(steering_angle)
        steering_vector_y = vehicle_forward_vector3D.x * math.sin(steering_angle) + vehicle_forward_vector3D.y * math.cos(steering_angle)

        steering_vector = carla.Vector3D(steering_vector_x*line_size, steering_vector_y*line_size, 1.5)
        steering_end_point = (steering_vector + vehicle_location)

        # self.logger.debug(f'vehicle_location : {vehicle_location}, end_point : {end_point}')

        vehicleAgent.world.debug.draw_line(vehicle_location, steering_end_point, life_time=0.5, color=carla.Color(0, 255, 0), thickness=0.2)
        vehicleAgent.world.debug.draw_line(vehicle_location, vehicle_forward_vector_end_point, life_time=0.5, color=carla.Color(255, 0, 0), thickness=0.2)


        pass