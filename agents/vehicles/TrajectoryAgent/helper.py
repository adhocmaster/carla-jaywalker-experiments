


import queue
import numpy as np
import pandas as pd


class HighD_Processor:

    @staticmethod
    def read_highD_data(path):
        # Read highD data from trajectory_list
        highD_data = pd.read_csv(path)
        return highD_data

    @staticmethod
    def read_stable_height_dict(path):
        stable_height = pd.read_csv(path)
        stable_height_dict = {}
        for i in range(len(stable_height)):
            stable_height_dict[stable_height.iloc[i,0]] = stable_height.iloc[i,1]
        return stable_height_dict

    @staticmethod
    def process_tracks(tracksDF):

        df = tracksDF
        grouped = df.groupby(['id'], sort=False)
        # Efficiently pre-allocate an empty list of sufficient size
        tracks = [None] * grouped.ngroups
        current_track = 0
        for group_id, rows in grouped:
            bounding_boxes = np.transpose(np.array([rows['x'].values,
                                                    rows['y'].values,
                                                    rows['width'].values,
                                                    rows['height'].values]))
            tracks[current_track] = {'id': np.int64(group_id),  # for compatibility, int would be more space efficient
                                        'frame': rows['frame'].values,
                                        'bbox': bounding_boxes,
                                        'xVelocity': rows['xVelocity'].values,
                                        'yVelocity': rows['yVelocity'].values,
                                        'xAcceleration': rows['xAcceleration'].values,
                                        'yAcceleration': rows['yAcceleration'].values,
                                        'frontSightDistance': rows['frontSightDistance'].values,
                                        'backSightDistance': rows['backSightDistance'].values,
                                        }
            current_track = current_track + 1
        return tracks

    @staticmethod
    def group_by_frame(tracksDf):
        df = tracksDf

        frame_queue = queue.Queue()
        grouped = df.groupby(['frame'], sort=False)
        for group_id, rows in grouped:
            # print('group ID row ', group_id, rows)
            bounding_boxes = np.transpose(np.array([rows['x'].values,
                                                    rows['y'].values,
                                                    rows['width'].values,
                                                    rows['height'].values]))
            ids = rows['id'].values
            frame_queue.put((ids, bounding_boxes))
        

        bboxs = frame_queue.get()
        # print(len(bboxs))

        return frame_queue

    # def draw_box(self, carla_bbox, color=carla.Color(255, 0, 0), life_time=0.06):
    #     self.debug.draw_box(carla_bbox, carla.Rotation(), 0.5, color, life_time)
    #     pass

    # def intersection(self, lst1, lst2):
    #     return list(set(lst1) & set(lst2))
    
    # def get_boxes_for_interpolate_frame(self, passed_time):
    #     passed_sec = int(passed_time)
    #     miliseconds = int((passed_time - passed_sec) * 1000)

    #     first_frame = int(25 * passed_time)
    #     second_frame = first_frame + 1

    #     print(passed_time, len(self.frame_list[first_frame]), len(self.frame_list[second_frame]))


    #     ids = self.intersection(self.frame_list[first_frame][0], self.frame_list[second_frame][0])
    #     # print(ids)
    #     interpolated_boxes = []
    #     for id in ids:
    #         # find index of the id in frame list first frame
    #         index_1 = np.where(self.frame_list[first_frame][0] == id)
    #         index_2 = np.where(self.frame_list[second_frame][0] == id)

    #         box1 = self.frame_list[first_frame][1][index_1]
    #         box2 = self.frame_list[second_frame][1][index_2]

    #         # print(box1, box2)
    #         distance = sqrt((box1[0][0] - box2[0][0])**2 + (box1[0][1] - box2[0][1])**2)
    #         # print(distance)
    #         # using 1D interpolation for box1 and box 2
    #         box = box1 + (box2 - box1) * (miliseconds/1000)
    #         interpolated_boxes.append(box)
    #         # print('elepsed time ', miliseconds)
    #         # print('first frame ', box1, 'second frame ', box2)
    #         # print('interpolated box', box)
        
    #     return interpolated_boxes




# self.tracks = HighD_Processor.read_highD_data(highD_path)

        # self.frame_queue = HighD_Processor.group_by_frame(self.tracks)
        # self.frame_list = list(self.frame_queue.queue)

        #  frame list a list of tuples (frame_id, bbox)
        # self.frame_list = frame_list

        # print('frame list ', self.frame_list[0])

        # self.world = world
        # self.debug = self.world.debug
        # self.pivot = pivot
        # self.start_time = time.time()
        # self.debug.draw_point(self.pivot.location, size=0.15, color=carla.Color(0,255,0), life_time=0.0, persistent_lines=True)
        




    # passed_time = time.time() - self.start_time
        # # self.interpolate_frame(passed_time)

        # # due to frame rate we had to interpolate the high d data 
        # # highD is 25 fps
        # # carla running in 16-19 fps (can we have fixed fps???)

        # # bboxs = self.frame_queue.get()[1]
        # bboxs_test = self.get_boxes_for_interpolate_frame(passed_time)

        # for box in bboxs_test:
        #     bbox = box[0]

        #     center_x = bbox[0] + bbox[2]/2
        #     center_y = bbox[1] + bbox[3]/2

        #     center_x = center_x + self.pivot.location.x
        #     center_y = center_y + self.pivot.location.y


        #     location = carla.Location(x=center_x, y=center_y, z=0)

        #     extent = carla.Vector3D(x=bbox[2]/2, y=bbox[3]/2, z=0)
        #     carla_bbox = carla.BoundingBox(location, extent)

        #     self.draw_box(carla_bbox, color=carla.Color(0, 255, 0), life_time=0.1)
            

        # # for bbox in bboxs:
        # #     center_x = bbox[0] + bbox[2]/2
        # #     center_y = bbox[1] + bbox[3]/2

        # #     center_x = center_x + self.pivot.location.x
        # #     center_y = center_y + self.pivot.location.y


        # #     location = carla.Location(x=center_x, y=center_y, z=0)

        # #     extent = carla.Vector3D(x=bbox[2]/2, y=bbox[3]/2, z=0)
        # #     carla_bbox = carla.BoundingBox(location, extent)

        # #     self.draw_box(carla_bbox)
        # # self.draw_box(self.trajectory_queue.get()[1])
            
        
        
            


