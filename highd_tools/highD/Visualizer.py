import copy
import os
import time
import cv2
import numpy as np
import pandas as pd

SCALE_FACTOR = 4 * 0.10106

import imageio
from PIL import Image

class Video():

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
            Video.draw_vehicle_with_id_over_image(image=image, 
                                                       tracks=tracks,
                                                       id=ego_id,
                                                       color=ego_color)
            # filter the other boxes
            tracks = tracks[tracks['id'] != ego_id]
            agent_ids = np.delete(agent_ids, np.where(agent_ids == ego_id))
        
        if target_id is not None and target_id in agent_ids:
            Video.draw_vehicle_with_id_over_image(image=image, 
                                                       tracks=tracks,
                                                       id=target_id,
                                                       color=target_color)
            # filter the other boxes
            tracks = tracks[tracks['id'] != target_id]
            agent_ids = np.delete(agent_ids, np.where(agent_ids == target_id))

        
        for id in agent_ids:
            Video.draw_vehicle_with_id_over_image(image=image, 
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
            img = Video.draw_frame(image=image,
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
            img = Video.draw_frame(image=image,
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
            img = Video.draw_frame(image=image,
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



class GIF():

    @staticmethod
    def draw_frame(image, tracks, frame_id,
                   ego_id=None, target_id=None,
                   ego_color=(255, 0, 0), target_color=(0, 255, 0), other_color=(0, 0, 255)):
        # Filter the frame data
        tracks = tracks[tracks['frame'] == frame_id]

        if len(tracks) == 0:
            print('invalid frame id')
            return

        # Deep copy of the image
        image = copy.deepcopy(image)

        agent_ids = tracks['id'].unique()

        def draw_vehicle(image, vehicle_data, color):
            df_bbox = vehicle_data[['x', 'y', 'width', 'height']]
            df_bbox = df_bbox / SCALE_FACTOR
            x = int(df_bbox['x'])
            y = int(df_bbox['y'])
            width = int(df_bbox['width'])
            height = int(df_bbox['height'])
            cv2.rectangle(image, (x, y), (x + width, y + height), color, 2)

        # Draw the frame number on the image
        cv2.putText(image, f"F: {frame_id}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        for id in agent_ids:
            vehicle_data = tracks[tracks['id'] == id]
            if ego_id is not None and id == ego_id:
                draw_vehicle(image, vehicle_data, ego_color)
            elif target_id is not None and id == target_id:
                draw_vehicle(image, vehicle_data, target_color)
            else:
                draw_vehicle(image, vehicle_data, other_color)

        return image

    @staticmethod
    def create_gif_from_frames(image,
                               combined_df,
                               start,
                               end,
                               fps=25,
                               gif_name=None,
                               output_dir=None):

        frameSize = image.shape[0:2][::-1]

        if gif_name is None:
            gif_name = str(int(round(time.time() * 1000))) + '.gif'
        else:
            gif_name = str(gif_name) + '.gif'

        print('creating gif with name ', gif_name)
        gif_path = os.path.join(output_dir, gif_name)

        images = []

        for i in range(start, end + 1):
            img = GIF.draw_frame(image=image,
                                        tracks=combined_df,
                                        frame_id=i,
                                        other_color=(255, 0, 255))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
            img = cv2.resize(img, frameSize)
            images.append(img)

        # Save the images as a GIF
        imageio.mimsave(gif_path, images, format='GIF', fps=fps)

    @staticmethod
    def create_gif_for_agent_with_target(image, tracks, 
                                         agent_id, target_id, 
                                         fps=25, output_dir=None, showBufferScene=False):

        df_ego = tracks[tracks['id'] == agent_id]
        df_target = tracks[tracks['id'] == target_id]

        temp_image = copy.deepcopy(image)
        frame_togather = tracks[(tracks['id'] == agent_id) & (tracks['precedingId'] == target_id)]['frame'].values

        if showBufferScene:
            start = min(int(df_ego['frame'].min()), int(df_target['frame'].min()))
            end = max(int(df_ego['frame'].max()), int(df_target['frame'].max()))
        else:
            start = frame_togather.min()
            end = frame_togather.max()

        print(f"start: {start}, end: {end} ")
        gif_name = f'ego_{agent_id}_pre_{target_id}_fr_{start}_to_{end}.gif'
        images = []

        for i in range(start, end + 1):
            img = GIF.draw_frame(image=temp_image,
                                        tracks=tracks,
                                        frame_id=i,
                                        ego_id=agent_id,
                                        target_id=target_id,
                                        ego_color=(0, 255, 0),
                                        target_color=(0, 0, 255),
                                        other_color=(255, 0, 255))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            images.append(pil_img)

        if output_dir is None:
            output_dir = os.getcwd()

        gif_path = os.path.join(output_dir, gif_name)
        images[0].save(gif_path, save_all=True, append_images=images[1:],
                       optimize=False, duration=int(1000/fps), loop=0)
        return gif_path
    
    @staticmethod
    def create_gif_for_agent(image, df, agent_id, 
                             fps=25, output_dir=None):

        df_ego = df[df['id'] == agent_id]
        start = min(df_ego['frame'])
        end = max(df_ego['frame'])

        print(f"agent id {agent_id} start: {start}, end: {end} total frames: {end - start} ")
        gif_name = f'agent_{agent_id}_fr_{start}_to_{end}.gif'
        images = []

        for i in range(start, end + 1):
            img = GIF.draw_frame(image=image, tracks=df, frame_id=i,
                                        ego_id=agent_id,
                                        ego_color=(0, 255, 0))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            images.append(pil_img)

        if output_dir is None:
            output_dir = os.getcwd()

        gif_path = os.path.join(output_dir, gif_name)
        images[0].save(gif_path, save_all=True, append_images=images[1:],
                       optimize=False, duration=int(1000/fps), loop=0)
        return gif_path

    @staticmethod
    def create_gif_for_agent_wheel_angle(image, df, agent_id, start_frame, end_frame, 
                             fps=25, output_dir=None):

        df_ego = df[(df['id'] == agent_id) & 
                    (df['frame'] >= start_frame) & 
                    (df['frame'] <= end_frame)]

        print(f"agent id {agent_id} start: {start_frame}, end: {end_frame} total frames: {end_frame - start_frame} ")
        gif_name = f'agent_{agent_id}_fr_{start_frame}_to_{end_frame}.gif'
        images = []

        for i in range(start_frame, end_frame + 1):
            img = GIF.draw_frame(image=image, tracks=df, frame_id=i,
                                        ego_id=agent_id,
                                        ego_color=(0, 255, 0))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            images.append(pil_img)

        if output_dir is None:
            output_dir = os.getcwd()

        gif_path = os.path.join(output_dir, gif_name)
        images[0].save(gif_path, save_all=True, append_images=images[1:],
                       optimize=False, duration=int(1000/fps), loop=0)
        return gif_path
