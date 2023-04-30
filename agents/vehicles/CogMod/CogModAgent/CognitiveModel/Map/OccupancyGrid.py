import numpy as np
import matplotlib.pyplot as plt

class Map():
    
    def __init__(self, x_size, y_size, resolution=0.1):
        self.x_size = x_size
        self.y_size = y_size
        self.resolution = resolution
        self.grid_size = x_size * y_size
        self.log_odds_prob = np.zeros((int(self.x_size / resolution), int(self.y_size / resolution)),order='C')
        self.log_occupied = 0.84
        self.log_free = 0.4
        self.curr_veh_pt = None
    
    def set_vehicle_pose(self, veh_pose):
        self.curr_veh_pt = veh_pose

    def visualize(self):
        print("The map \n" + str(self.log_odds_prob))
        plt.scatter(self.curr_veh_pt[0], self.curr_veh_pt[1], s=20)
        plt.imshow(self.log_odds_prob, interpolation ='none', cmap = 'binary')
        plt.show()
    
    def update_log_odds(self, x, y, occupied = True):
        loc_present = [int(x/self.resolution),int(y/self.resolution)]
        x,y = loc_present
        if occupied == True:
            self.log_odds_prob[x, y] = self.log_odds_prob[x, y] + self.log_occupied
            if self.log_odds_prob[x, y] > 3.5:
                self.log_odds_prob[x, y] = 3.5
        else:
            self.log_odds_prob[x, y] = self.log_odds_prob[x, y] - self.log_free
            if self.log_odds_prob[x, y] < -2:
                self.log_odds_prob[x, y] = -2

if __name__ == "__main__":
    env_map = Map(10,100, resolution=1)
    env_map.set_vehicle_pose([5,5])
    for i in range(10):
        env_map.update_log_odds(i, i, occupied=True)
    
    env_map.visualize()
