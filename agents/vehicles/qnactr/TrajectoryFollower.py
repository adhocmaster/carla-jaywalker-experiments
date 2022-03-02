



class TrajectoryFollower():
    def __init__(self, id, vehicle, trajectory=None):
        super().__init__()
        self.name = "TrajectoryFollower"
        if trajectory is None or vehicle is None:
            return
        self.id = id
        self.trajectory = trajectory
        self.vehicle = vehicle

        # disable physics
        self.vehicle.set_simulate_physics(False)
        self.simulation_time = 0
        print('creating TrajectoryFollower')


    def update_agent(self):
        
        pass