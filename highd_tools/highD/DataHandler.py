#  this script try to access the data from the dill folder
#  if the data is not there, it will read the data from the csv files 
#  and save it to the dill folder


from .DataContainer import DataContainer
from .HighD import HighD
from .config import *
import pandas as pd
import cv2
import os
import numpy as np
import dill




def read_image(image_path):
    return cv2.imread(image_path)

def read_recordingMeta_csv(recordingMeta_path):
    df_obj = pd.read_csv(recordingMeta_path)
    return df_obj

def read_trackMeta_csv(tracksMeta_path):
    df_obj = pd.read_csv(tracksMeta_path)
    return df_obj

def read_track_csv(tracks_path):
    df_obj = pd.read_csv(tracks_path)
    return df_obj


def get_path_dict(folder_path):

    image_id = '_highway.png'
    meta_id = '_recordingMeta.csv'
    track_meta_id = '_tracksMeta.csv'
    track_id = '_tracks.csv'

    path_dict = {}
    for i in range(1, 61):
        if i < 10:
            id = '0' + str(i)
        else:
            id = str(i)
        image_path =  os.path.join(folder_path, id + image_id)
        recordingMeta_path = os.path.join(folder_path, id + meta_id)
        tracksMeta_path = os.path.join(folder_path, id + track_meta_id)
        tracks_path = os.path.join(folder_path, id + track_id)

        path_object = {
            'image_path': image_path,
            'recordingMeta_path': recordingMeta_path,
            'tracksMeta_path': tracksMeta_path,
            'tracks_path': tracks_path
        }

        path_dict[i] = path_object
    
    # print(path_dict)

    return path_dict
    pass

def read_highD_data(pathObj):
    
    image_path = pathObj['image_path']
    recordingMeta_path = pathObj['recordingMeta_path']
    tracksMeta_path = pathObj['tracksMeta_path']
    tracks_path = pathObj['tracks_path']

    img = read_image(image_path)
    recordingMeta = read_recordingMeta_csv(recordingMeta_path)
    tracksMeta = read_trackMeta_csv(tracksMeta_path)
    tracks = read_track_csv(tracks_path)

    recordingMeta_dict = process_recordingMeta(recordingMeta)
    tracksMeta_dict = process_tracksMeta(tracksMeta)
    tracks_dict = process_tracks(tracks)

    data_container = DataContainer(id=recordingMeta_dict['id'],
                                   image=img,
                                   recordingMeta=recordingMeta,
                                   tracksMeta=tracksMeta,
                                   tracks=tracks,
                                   recordingMeta_dict=recordingMeta_dict,
                                   tracksMeta_dict=tracksMeta_dict,
                                   tracks_dict=tracks_dict)

    return data_container

# this function reads the given list of dataset from the highD dataset
#  total 60 datasets are available. ID list needs to be in the range of 1 to 60
def read_dataset(id_list, data_directory=None):
    
    if data_directory is None:
        data_directory = DATA_DIRECTORY
    
    highD_list = []
    path_dict = get_path_dict(data_directory)
    
    dill_folder_name = 'dill'

    for id in id_list:
        if id < 1 or id > 60:
            print('id must be between 1 and 60')
            return
        
        # creating directory if not exist 
        isExist = os.path.exists(dill_folder_name)
        if not isExist:
            os.mkdir(dill_folder_name)
        

        dill_path = os.path.join(dill_folder_name, str(id) + '.dill')
        try:
            ifile = open(dill_path, "rb")
            data_container = dill.load(ifile)
            ifile.close()
        except:
            print('dill not found for id: ', id)
            data_container = read_highD_data(path_dict[id])
            ofile = open(dill_path, "wb")
            dill.dump(data_container, ofile)
            ofile.close()

        highD = HighD(data_container)
        highD_list.append(highD)

    return highD_list

def process_recordingMeta(recordingMetaDF):

    df = recordingMetaDF
    extracted_meta_dictionary = {'id': int(df['id'][0]),
                                'frameRate': int(df['frameRate'][0]),
                                'locationId': int(df['locationId'][0]),
                                'speedLimit': float(df['speedLimit'][0]),
                                'month': str(df['month'][0]),
                                'weekDay': str(df['weekDay'][0]),
                                'startTime': str(df['startTime'][0]),
                                'duration': float(df['duration'][0]),
                                'totalDrivenDistance': float(df['totalDrivenDistance'][0]),
                                'totalDrivenTime': float(df['totalDrivenTime'][0]),
                                'numVehicles': int(df['numVehicles'][0]),
                                'numCars': int(df['numCars'][0]),
                                'numTrucks': int(df['numTrucks'][0]),
                                'upperLaneMarkings': np.fromstring(df['upperLaneMarkings'][0], sep=";"),
                                'lowerLaneMarkings': np.fromstring(df['lowerLaneMarkings'][0], sep=";")}

    return extracted_meta_dictionary




def process_tracksMeta(tracksMetaDF):
    df = tracksMetaDF
    static_dictionary = {}
    for i_row in range(df.shape[0]):
        track_id = int(df['id'][i_row])
        static_dictionary[track_id] = {'id': track_id,
                                        'width': int(df['width'][i_row]),
                                        'height': int(df['height'][i_row]),
                                        'initialFrame': int(df['initialFrame'][i_row]),
                                        'finalFrame': int(df['finalFrame'][i_row]),
                                        'numFrames': int(df['numFrames'][i_row]),
                                        'class': str(df['class'][i_row]),
                                        'drivingDirection': float(df['drivingDirection'][i_row]),
                                        'traveledDistance': float(df['traveledDistance'][i_row]),
                                        'minXVelocity': float(df['minXVelocity'][i_row]),
                                        'maxXVelocity': float(df['maxXVelocity'][i_row]),
                                        'meanXVelocity': float(df['meanXVelocity'][i_row]),
                                        'minDHW': float(df['minDHW'][i_row]),
                                        'minTHW': float(df['minTHW'][i_row]),
                                        'minTTC': float(df['minTTC'][i_row]),
                                        'numLaneChanges': int(df['numLaneChanges'][i_row]),
                                        }
    return static_dictionary



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
                                    'thw': rows['thw'].values,
                                    'ttc': rows['ttc'].values,
                                    'dhw': rows['dhw'].values,
                                    'precedingXVelocity': rows['precedingXVelocity'].values,
                                    'precedingId': rows['precedingId'].values,
                                    'followingId': rows['followingId'].values,
                                    'leftFollowingId': rows['leftFollowingId'].values,
                                    'leftAlongsideId': rows['leftAlongsideId'].values,
                                    'leftPrecedingId': rows['leftPrecedingId'].values,
                                    'rightFollowingId': rows['rightFollowingId'].values,
                                    'rightAlongsideId': rows['rightAlongsideId'].values,
                                    'rightPrecedingId': rows['rightPrecedingId'].values,
                                    'laneId': rows['laneId'].values
                                    }
        current_track = current_track + 1
    return tracks
