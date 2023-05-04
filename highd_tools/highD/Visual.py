import copy
import os
import time
import cv2
import numpy as np
import pandas as pd

SCALE_FACTOR = 4 * 0.10106

class Visualizer():

    #  this method draws the vehicle bounding box on the provided highway image
    #  @param image: the highway image
    #  @param track: the tracks object
    #  @param frame_id: the frame id to draw from the tracks object
    #  @param ego_id: the id of the ego vehicle to draw from the tracks object
    #  @param target)id: the id of the target vehicle to draw from the tracks object
    #  @param ego_color: the color to draw the ego vehicle bounding box
    #  @param target_color: the color to draw the target vehicle bounding box
    #  @param other_color: the color of the bounding box of the other vehicles
    #  @return: the image with the bounding boxes drawn
    @staticmethod
    def draw_frame(image, 
                   tracks,
                   frame_id, 
                   ego_id=None,
                   target_id=None,
                   ego_color=(255, 0, 0),
                   target_color=(0, 255, 0),
                   other_color=(0, 0, 255)):

        # filter the frame data 
        tracks = tracks[tracks['frame'] == frame_id]

        if len(tracks) == 0:
            print('invalid frame id')
            return

        #  deep copy of the image
        image = copy.deepcopy(image)

        agent_ids = tracks['id'].unique()

        if ego_id is not None and ego_id in agent_ids:
            Visualizer.draw_vehicle_with_id_over_image(image=image, 
                                                       tracks=tracks,
                                                       id=ego_id,
                                                       color=ego_color)
            # filter the other boxes
            tracks = tracks[tracks['id'] != ego_id]
            agent_ids = np.delete(agent_ids, np.where(agent_ids == ego_id))
        
        if target_id is not None and target_id in agent_ids:
            Visualizer.draw_vehicle_with_id_over_image(image=image, 
                                                       tracks=tracks,
                                                       id=target_id,
                                                       color=target_color)
            # filter the other boxes
            tracks = tracks[tracks['id'] != target_id]
            agent_ids = np.delete(agent_ids, np.where(agent_ids == target_id))

        
        for id in agent_ids:
            Visualizer.draw_vehicle_with_id_over_image(image=image, 
                                                       tracks=tracks,
                                                       id=id,
                                                       color=other_color)
            tracks = tracks[tracks['id'] != ego_id]
            agent_ids = np.delete(agent_ids, np.where(agent_ids == id))

        return image


    #  this methods draws one bounding box on the image
    def draw_vehicle_with_id_over_image(image, 
                                        tracks, 
                                        id, 
                                        color=(255, 0, 0)):

        df_vehicle = tracks[tracks['id'] == id]
        df_bbox = df_vehicle[['x', 'y', 'width', 'height']]
        df_bbox = df_bbox / SCALE_FACTOR
        x = int(df_bbox['x'])
        y = int(df_bbox['y'])
        width = int(df_bbox['width'])
        height = int(df_bbox['height'])
        cv2.rectangle(image, (x, y), (x+width, y+height), color, 2)
        pass


    #  this method create a video from the dataset
    #  @param start: the start frame
    #  @param end: the end frame
    #  @param fps: the fps of the video
    #  @param video_name: the name of the video
    #  @param ego_id: the id of the ego vehicle
    #  @param output_dir: the output directory
    @staticmethod
    def create_video_from_frames(image,
                                 tracks,
                                 start, 
                                 end, 
                                 fps=25, 
                                 video_name=None, 
                                 output_dir=None):

        frameSize = image.shape[0:2][::-1]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if video_name is None:
            video_name = str(int(round(time.time() * 1000))) + '.avi'
        else:
            video_name = str(video_name) + '.avi'
        print('creating video with name ', video_name)
        out = cv2.VideoWriter(os.path.join(output_dir, video_name), fourcc, fps, frameSize)
        for i in range(start, end + 1):
            img = Visualizer.draw_frame(image=image,
                                        tracks=tracks,
                                        frame_id=i,
                                        other_color=(255, 0, 255))
            img = cv2.resize(img, frameSize)
            out.write(img)
        out.release()
        
        pass

    
    @staticmethod
    def create_video_for_agent(image,
                               tracks,
                               tracksMeta,
                               agent_id,
                               fps=25,
                               video_name=None,
                               output_dir=None):
        frameSize = image.shape[0:2][::-1]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if video_name is None:
            video_name = str(int(round(time.time() * 1000))) + '.avi'
        else:
            video_name = str(video_name) + '.avi'
        print('creating video with name ', video_name)

        df = tracksMeta[tracksMeta['id'] == agent_id]
        start = int(df['initialFrame'])
        end = int(df['finalFrame'])
        
        print(start, end)
        out = cv2.VideoWriter(os.path.join(output_dir, video_name), fourcc, fps, frameSize)

        for i in range(start, end + 1):
            img = Visualizer.draw_frame(image=image,
                                        tracks=tracks,
                                        frame_id=i,
                                        ego_id=agent_id,
                                        ego_color=(0, 255, 0),
                                        other_color=(255, 0, 255))
            img = cv2.resize(img, frameSize)
            out.write(img)

        out.release()

        pass

    @staticmethod
    def create_video_for_agent_with_target(image,
                                           tracks,
                                           tracksMeta,
                                           agent_id,
                                           target_id,
                                           fps=25,
                                           video_name=None,
                                           output_dir=None):
        frameSize = image.shape[0:2][::-1]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if video_name is None:
            video_name = str(int(round(time.time() * 1000))) + '.avi'
        else:
            video_name = str(video_name) + '.avi'
        print('creating video with name ', video_name)

        df_ego = tracksMeta[tracksMeta['id'] == agent_id]
        df_target = tracksMeta[tracksMeta['id'] == target_id]

        start = min(int(df_ego['initialFrame']), int(df_target['initialFrame']))
        end = max(int(df_ego['finalFrame']), int(df_target['finalFrame']))
        
        print(start, end)
        out = cv2.VideoWriter(os.path.join(output_dir, video_name), fourcc, 25, frameSize)

        for i in range(start, end + 1):
            img = Visualizer.draw_frame(image=image,
                                        tracks=tracks,
                                        frame_id=i,
                                        ego_id=agent_id,
                                        target_id=target_id,
                                        ego_color=(0, 255, 0),
                                        target_color=(0, 0, 255),
                                        other_color=(255, 0, 255))
            img = cv2.resize(img, frameSize)
            out.write(img)

        out.release()

        pass


    @staticmethod
    def draw_lane_marking_from_dataset(img, recordingMeta):

        uLaneMark = recordingMeta['upperLaneMarkings']
        lLaneMark = recordingMeta['lowerLaneMarkings']

        uLaneMark = uLaneMark[0].split(';')
        lLaneMark = lLaneMark[0].split(';')

        uLaneMark = [float(i) for i in uLaneMark]
        lLaneMark = [float(i) for i in lLaneMark]

        uLaneMark = np.array(uLaneMark)
        lLaneMark = np.array(lLaneMark)

        uLaneMark = uLaneMark / SCALE_FACTOR
        lLaneMark = lLaneMark / SCALE_FACTOR

        uLaneMark = uLaneMark.astype(int)
        lLaneMark = lLaneMark.astype(int)

        print(uLaneMark, lLaneMark)

        image = copy.deepcopy(img)
        height, width, _ = image.shape
        for i in uLaneMark:
            cv2.line(image, (0, i), (width, i), (255, 0, 0), 1)
        for i in lLaneMark:
            cv2.line(image, (0, i), (width, i), (0, 0, 255), 1)

        return image

    # @staticmethod
    # def create_video_car_follow_maneuver(self):
    #     if self.car_follow is None:
    #         self.car_follow = self.filter_car_following()
        
    #     for i in range(len(self.car_follow)):
            
    #         ego_id = self.car_follow[i]['ego_id']
    #         pred_id = self.car_follow[i]['pred_id']

    #         video_name = str(self.id) + '_car_follow_' + str(ego_id) + '_' + str(pred_id)

    #         start = self.car_follow[i]['following_start']
    #         end = self.car_follow[i]['following_end']

    #         self.create_video_from_frames(start, end, 25, video_name, ego_id)
    #     pass
