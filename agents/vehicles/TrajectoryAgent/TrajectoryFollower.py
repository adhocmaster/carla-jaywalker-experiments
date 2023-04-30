import carla

class TrajectoryFollower():
    # This class is used to follow a trajectory
    # The trajectory is a list of [frame, x, y, speed]
    def __init__(self, vehicle, trajectory_df, pivot, agent_id, stable_height, lane_id):
        self.vehicle = vehicle
        self.trajectory = trajectory_df
        self.pivot = pivot
        self.agent_id = agent_id
        self.stable_height = stable_height

        self.velocity = 0

        self.left_lane_id = lane_id["left_lane"]
        self.right_lane_id = lane_id["right_lane"]

        self.vehicle.set_simulate_physics(False)
        
        minFrame = self.trajectory["frame"].min()
        self.run_step(minFrame)
        pass

    def destroy(self):
        self.vehicle.destroy()
        pass

    def get_velocity(self):
        return self.velocity

    def get_vehicle(self):
        return self.vehicle


    # frame id starts from the original frame id from the highd dataset
    def run_step(self, frame_id):
        # get the x y and speed from the trajectory
        cur_row = self.trajectory[self.trajectory["frame"] == frame_id]
        center_x, center_y = self.transform_coordinate_wrt_pivot(cur_row)
        location, rotation = self.get_vehicle_transform(cur_row, center_x, center_y, self.stable_height)
        cur_destination_transform = carla.Transform(location, rotation)
        self.vehicle.set_transform(cur_destination_transform)
        self.velocity =  carla.Vector3D(x=cur_row["xVelocity"].values[0], y=cur_row["yVelocity"].values[0], z=0)
        
        # print('velocity +++++++++ ', self.velocity)
        pass

    def is_done(self, frame_id):
        max_frame = self.trajectory["frame"].max()
        if frame_id >= max_frame:
            return True
        else:
            return False

    
        
    def get_destination_transform(self):
        max_frame = self.trajectory["frame"].max()
        cur_row = self.trajectory[self.trajectory["frame"] == max_frame]
        center_x, center_y = self.transform_coordinate_wrt_pivot(cur_row)
        location, rotation = self.get_vehicle_transform(cur_row, center_x, center_y, self.stable_height)
        cur_destination_transform = carla.Transform(location, rotation)
        return cur_destination_transform

    def transform_coordinate_wrt_pivot(self, row):
        x, y, width, height = row["x"], row["y"], row["width"], row["height"]
        center_x = x + width/2
        center_y = y + height/2
        center_x = center_x + self.pivot.location.x
        center_y = center_y + self.pivot.location.y
        return float(center_x), float(center_y)

    def get_vehicle_transform(self, row, center_x, center_y, height):

        # location = carla.Location(x=center_x, y=center_y, z=height)
        location = carla.Location(x=center_x, y=center_y, z=height)
        laneID = int(row["laneId"])
        rotation = carla.Rotation(yaw=180)

        if laneID in self.left_lane_id:
            rotation = carla.Rotation(yaw=0)
        return location,rotation

    

