
import copy
import time
import cv2
import imageio
import os
from PIL import Image

SCALE_FACTOR = 4 * 0.10106


class Visualizer():

    @staticmethod
    def draw_frame(image,
                tracks,
                frame_id,
                ego_id=None,
                target_id=None,
                ego_color=(255, 0, 0),
                target_color=(0, 255, 0),
                other_color=(0, 0, 255)):
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
        cv2.putText(image, f"F: {frame_id}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

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
            img = Visualizer.draw_frame(image=image,
                                        tracks=combined_df,
                                        frame_id=i,
                                        other_color=(255, 0, 255))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
            img = cv2.resize(img, frameSize)
            images.append(img)

        # Save the images as a GIF
        imageio.mimsave(gif_path, images, format='GIF', fps=fps)

    @staticmethod
    def create_gif_for_agent_with_target(image, tracks, tMeta, agent_id, target_id, fps=25, output_dir=None):

        df_ego = tMeta[tMeta['id'] == agent_id]
        df_target = tMeta[tMeta['id'] == target_id]

        start = min(int(df_ego['initialFrame'].iloc[0]),
                    int(df_target['initialFrame'].iloc[0]))
        end = max(int(df_ego['finalFrame'].iloc[0]), int(df_target['finalFrame'].iloc[0]))

        print(f"start: {start}, end: {end} ")
        gif_name = f'ego_{agent_id}_pre_{target_id}_fr_{start}_to_{end}.gif'
        images = []

        for i in range(start, end + 1):
            img = Visualizer.draw_frame(image=image,
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
        images[0].save(gif_path, save_all=True, append_images=images[1:], optimize=False, duration=int(1000/fps), loop=0)
        return gif_path