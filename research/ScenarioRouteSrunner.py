from srunner.scenarioconfigs.route_scenario_configuration import RouteScenarioConfiguration
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenarios.route_scenario import RouteScenario, convert_transform_to_location, interpolate_trajectory

from srunner.scenariomanager.scenarioatomics.atomic_criteria import (CollisionTest,
                                                                     InRouteTest,
                                                                     RouteCompletionTest,
                                                                     OutsideRouteLanesTest,
                                                                     RunningRedLightTest,
                                                                     RunningStopTest,
                                                                     ActorSpeedAboveThresholdTest)
from srunner.tools.route_parser import RouteParser
from lib import LoggerFactory
import logging

class ScenarioRouteSrunner(RouteScenario):

    def __init__(self, world, config, debug_mode=False, criteria_enable=True, timeout=300):
        """
        Setup all relevant parameters and create scenarios along route
        """

        self.name = "ScenarioRouteSrunner"
        self.logger = LoggerFactory.getBaseLogger(self.name, defaultLevel=logging.INFO, file="./logs/ScenarioRouteSrunner.log") # TODO update

        super(ScenarioRouteSrunner, self).__init__(
                                            world=world,
                                            config=config,
                                            debug_mode=False,
                                            criteria_enable=criteria_enable,
                                            timeout=timeout)


    def _update_route(self, world, config: RouteScenarioConfiguration, debug_mode):
        """
        Update the input route, i.e. refine waypoint list, and extract possible scenario locations

        Parameters:
        - world: CARLA world
        - config: Scenario configuration (RouteConfiguration)
        """

        # Transform the scenario file into a dictionary
        world_annotations = RouteParser.parse_annotations_file(config.scenario_file)

        # prepare route's trajectory (interpolate and add the GPS route)
        gps_route, route = interpolate_trajectory(config.trajectory)

        # print("_update_route", [str(wpTuple[0].location) for wpTuple in route])
        # exit(0)

        potential_scenarios_definitions, _ = RouteParser.scan_route_for_scenarios(config.town, route, world_annotations)

        self.route = route
        CarlaDataProvider.set_ego_vehicle_route(convert_transform_to_location(self.route))

        if config.agent is not None:
            config.agent.set_global_plan(gps_route, self.route)

        # Sample the scenarios to be used for this route instance.
        self.sampled_scenarios_definitions = self._scenario_sampling(potential_scenarios_definitions)

        # Timeout of scenario in seconds
        self.timeout = self._estimate_route_timeout()

        # Print route in debug mode
        self._draw_waypoints(world, self.route, vertical_shift=0.1, persistency=50000.0)
        # if debug_mode:
        #     self._draw_waypoints(world, self.route, vertical_shift=0.1, persistency=50000.0)
            
    def _create_test_criteria(self):
        """
        """

        criteria = []

        route = convert_transform_to_location(self.route)

        collision_criterion = CollisionTest(self.ego_vehicles[0], terminate_on_failure=False)

        route_criterion = InRouteTest(self.ego_vehicles[0],
                                      route=route,
                                      offroad_max=30,
                                      terminate_on_failure=True)

        print("_create_test_criteria", route)

        completion_criterion = RouteCompletionTest(self.ego_vehicles[0], route=route)

        outsidelane_criterion = OutsideRouteLanesTest(self.ego_vehicles[0], route=route)

        red_light_criterion = RunningRedLightTest(self.ego_vehicles[0])

        stop_criterion = RunningStopTest(self.ego_vehicles[0])

        blocked_criterion = ActorSpeedAboveThresholdTest(self.ego_vehicles[0],
                                                         speed_threshold=0.1,
                                                         below_threshold_max_time=90.0,
                                                         terminate_on_failure=True)

        criteria.append(completion_criterion)
        criteria.append(collision_criterion)
        criteria.append(route_criterion)
        criteria.append(outsidelane_criterion)
        criteria.append(red_light_criterion)
        criteria.append(stop_criterion)
        criteria.append(blocked_criterion)

        return criteria

        

    def remove_all_actors(self):
        """
        Remove all actors
        """
        if self.other_actors is None:
            self.logger.warning("Scenario does not contain other actors. Must be something wrong")
            return
        for i, _ in enumerate(self.other_actors):
            if self.other_actors[i] is not None:
                if CarlaDataProvider.actor_id_exists(self.other_actors[i].id):
                    CarlaDataProvider.remove_actor_by_id(self.other_actors[i].id)
                self.other_actors[i] = None
        self.other_actors = []