
# def find_car_following(meta_data, 
#                        data, 
#                        ego_type, 
#                        preceding_type, 
#                        thw_lower_bound=0, 
#                        thw_upper_bound=6):
#     """
#     Find out car-following situations from specific vehicle types

#     :param meta_data: track meta information from highD dataset
#     :param data: track data from highD dataset
#     :param my_type: the ego vehicle's type
#     :param preceding_type: the preceding vehicle's type

#     :return: a list of dictionary with
#         ego_id: identification of the ego vehicle
#         pred_id: identification of the preceding vehicle
#         following_start: the frame when the following starts
#         following_duration: the following duration
#         following_end: the frame when the following ends
#         dhw: array of DHW while following
#         thw: array of THW while following
#         ttc: array of TTC while following
#         TET: duration in seconds while TTC < TTC_STAR
#     """
#     following_data = []
#     for i in range(0, len(data)):
#         following_started = False
#         following_dhw = []
#         following_thw = []
#         following_ttc = []
#         ego_speed = []
#         pred_speed = []
#         frame_following_start = 0
#         following_duration = 0
#         prev_preceding_id = 0
#         ego_id = data[i].get('id')
#         for frame in range(0, len(data[i].get('frame'))):
#             thw = data[i].get('thw')[frame]
#             # if there is a vehicle at the front and the time gap between vehicle is inside the bound
#             if (check_thw(thw, thw_lower_bound, thw_upper_bound)):
#             # if (data[i].get('precedingId')[frame] != 0 and (CF_TGAP_LOWER_BOUND < data[i].get('thw')[frame] < CF_TGAP_UPPER_BOUND)):
#                 cur_preceding_id = data[i].get('precedingId')[frame]
#                 # this condition means that the lead vehicle has changed
#                 if prev_preceding_id != 0 and cur_preceding_id != prev_preceding_id and following_started:
#                     # the preceding vehicle changed in the current frame
#                     # so the car follow situation ends. we save the data and reset variables 
#                     frame_following_end = data[i].get('frame')[frame] - 1
#                     # this condition ensures that the follow situation is at least 2 frames long
#                     if frame_following_end != frame_following_start:
#                         #  we save the data 
#                         following_data.append(
#                             {"ego_id": ego_id, "pred_id": prev_preceding_id, "following_start": frame_following_start,
#                              "following_duration": following_duration, "following_end": frame_following_end,
#                              "dhw": statistics.mean(following_dhw), "thw": np.nanmean(following_thw),
#                              "ttc": statistics.mean(following_ttc),
#                              "TET":  (sum(map(lambda x: x <= TTC_STAR, following_ttc)))*TIME_STEP,
#                              "ego_speed": ego_speed, "pred_speed": pred_speed})
                    
#                     # we reset all the variables in either case 
#                     following_started = False
#                     following_dhw = []
#                     following_thw = []
#                     following_ttc = []
#                     ego_speed = []
#                     pred_speed = []
#                     frame_following_start = 0
#                     following_duration = 0
                
#                 # assign the preceding vehicle
#                 prev_preceding_id = cur_preceding_id

#                 # if the interaction is of given type (car - car, car - truck, truck - car, truck - truck)
#                 if check_interaction_type(meta_data, ego_id, ego_type, prev_preceding_id, preceding_type):

#                     #  if the car following has not started yet, we start it
#                     if following_started is False:
#                         following_started = True
#                         frame_following_start = data[i].get('frame')[frame]

#                     dhw = data[i].get('dhw')[frame]
#                     ego_velocity = data[i].get('xVelocity')[frame]
#                     preceding_velocity = data[i].get('precedingXVelocity')[frame]

#                     if dhw > 0:
#                         following_dhw.append(dhw)
#                         following_ttc.append(get_ttc(dhw, ego_velocity, preceding_velocity))

#                     if data[i].get('thw')[frame] > 0:
#                         following_thw.append(data[i].get('thw')[frame])
#                     else:
#                         following_thw.append(np.nan)
#                     ego_speed.append(data[i].get('xVelocity')[frame])
#                     pred_speed.append(data[i].get('precedingXVelocity')[frame])
#                     following_duration = following_duration + 1
                    
#             # if there is not a vehicle at the front or the time gap is outside the bound
#             else:
#                 # check if we were recording a following situation
#                 if following_started is True:
#                     # if yes, then assign the end of the following situation frame with the last frame
#                     frame_following_end = data[i].get('frame')[frame] - 1
#                     # check if the follow situation is a valid one
#                     #  valid follow situation should have at least 2 frames
#                     if frame_following_end != frame_following_start:
#                         # record the follow situation
#                         following_data.append(
#                             {"ego_id": ego_id, "pred_id": prev_preceding_id, "following_start": frame_following_start,
#                              "following_duration": following_duration, "following_end": frame_following_end,
#                              "dhw": statistics.mean(following_dhw), "thw": np.nanmean(following_thw),
#                              "ttc": statistics.mean(following_ttc),
#                              "TET": (sum(map(lambda x: x <= TTC_STAR, following_ttc))) * TIME_STEP,
#                              "ego_speed": ego_speed, "pred_speed": pred_speed})
                    
#                     # reset the variables
#                     following_started = False
#                     following_dhw = []
#                     following_thw = []
#                     following_ttc = []
#                     ego_speed = []
#                     pred_speed = []
#                     frame_following_start = 0
#                     following_duration = 0
#                     prev_preceding_id = 0
#     return following_data



# def check_interaction_type(meta_data, ego_id, ego_type, preceding_id, preceding_type):
#     # if the interaction is of given type (car - car, car - truck, truck - car, truck - truck)
#     return (get_vehicle_class(meta_data, preceding_id) == preceding_type) and (get_vehicle_class(meta_data, ego_id) == ego_type)

# def check_thw(thw, thw_lower_bound, thw_upper_bound):
#     # time headway should be within the given bound and non zero
#     return thw != 0 and (thw_lower_bound < thw < thw_upper_bound)


# def get_vehicle_class(meta_data, id):
#     """

#     :param meta_data: track meta information from highD dataset
#     :param id: vehicle's id in the dataset
#     :return: vehicle type (string: 'Car' or 'Truck')
#     """
#     return meta_data[id].get('class')


# def get_ttc(dhw, my_speed, pred_speed):
#     my_speed = abs(my_speed)
#     pred_speed = abs(pred_speed)
#     # ego is faster than the preceding vehicle so ttc will be decresing
#     if my_speed > pred_speed and dhw != 0:
#         velocity_diff = my_speed - pred_speed
#         return dhw / velocity_diff
#     else:
#         return np.nan

# class LaneChange():
#     def find_lane_changes(meta_data, data):
#         """
#         Find out lane-changing situations from the dataset

#         :param meta_data: track meta information from highD dataset
#         :param data: track data from highD dataset

#         :return: a list of dictionary with
#             sumLC: total number of lane changes
#             carLC: total number of lane changes by cars
#             truckLC: total number of lane changes by trucks
#             totalCar: total number of cars
#             totalTruck: total number of trucks
#         """
#         n_car = 0
#         n_car_lc = 0
#         n_truck = 0
#         n_truck_lc = 0
#         for i in range(0, len(data)):
#             ego_id = data[i].get('id')
#             n_lc = meta_data[ego_id].get('numLaneChanges')
#             vtype = meta_data[ego_id].get('class')
#             if vtype == "Car":
#                 n_car_lc = n_car_lc + n_lc
#                 n_car = n_car + 1
#             elif vtype == "Truck":
#                 n_truck_lc = n_truck_lc + n_lc
#                 n_truck = n_truck + 1
#             else:
#                 print("vehicle class unknown")
#         n_total_lc = n_car_lc + n_truck_lc
#         lc_data = {
#             "sumLC": n_total_lc,
#             "carLC": n_car_lc,
#             "truckLC": n_truck_lc,
#             "totalCar": n_car,
#             "totalTruck": n_truck
#         }
#         return lc_data


#     def get_lane_change_trajectory(meta_data, data):
        
#         y_accel_car_LC = []
#         y_accel_truck_LC = []
#         y_accel_car_noLC = []
#         y_accel_truck_noLC = []
#         y_pos_car_LC = []
#         y_pos_car_noLC = []
#         y_pos_truck_LC = []
#         y_pos_truck_noLC = []
#         y_speed_car_LC = []
#         y_speed_car_noLC = []
#         y_speed_truck_LC = []
#         y_speed_truck_noLC = []
#         for i in range(0, len(data)):
#             ego_id = data[i].get('id')
#             n_lc = meta_data[ego_id].get('numLaneChanges')
#             vtype = meta_data[ego_id].get('class')
#             if n_lc > 0:
#                 # this vehicle changes lane
#                 # find lane change frame index
#                 LC_index = []
#                 totalFrames = len(data[i].get('laneId'))
#                 lane_ids = list(data[i].get('laneId'))
#                 current_lane = lane_ids[0]
#                 for j in range(0, totalFrames):
#                     if lane_ids[j] != current_lane:
#                         LC_index.append(j)
#                         current_lane = lane_ids[j]
#                 for index in LC_index:
#                     if LC_MARGIN_FRAMES < index < (totalFrames - LC_MARGIN_FRAMES):
#                         lower_bound = index - LC_MARGIN_FRAMES
#                         upper_bound = index + LC_MARGIN_FRAMES
#                         if vtype == "Car":
#                             y_accel_car_LC += list(data[i].get('yAcceleration')[lower_bound:upper_bound])
#                             y_speed_car_LC += list(data[i].get('yVelocity')[lower_bound:upper_bound])
#                             y_pos_car_LC = list(data[i].get('bbox')[:, 1][lower_bound:upper_bound])
#                             # plt.plot(data[i].get('y'))
#                             # plt.axvline(x=index)
#                             # plt.show()
#                         elif vtype == "Truck":
#                             y_accel_truck_LC += list(data[i].get('yAcceleration')[lower_bound:upper_bound])
#                             y_speed_truck_LC += list(data[i].get('yVelocity')[lower_bound:upper_bound])
#                             y_pos_truck_LC = list(data[i].get('bbox')[:, 1][lower_bound:upper_bound])
#                         else:
#                             print("vehicle class unknown")
#             else:
#                 # this vehicle did not change lane
#                 # find out average yAcceleration
#                 # this vehicle changes lane
#                 if vtype == "Car":
#                     y_accel_car_noLC += list(data[i].get('yAcceleration'))
#                     y_speed_car_noLC += list(data[i].get('yVelocity'))
#                     # y_pos_car_noLC = list(data[i].get('y'))    # data[i].get('bbox')[0][0]
#                     y_pos_car_noLC = list(data[i].get('bbox')[:, 1])    # data[i].get('bbox')[0][0]
#                 elif vtype == "Truck":
#                     # if absolute value is desired >> [abs(a) for a in list(data[i].get('yAcceleration'))]
#                     y_accel_truck_noLC += list(data[i].get('yAcceleration'))
#                     y_speed_truck_noLC += list(data[i].get('yVelocity'))
#                     # y_pos_truck_noLC = list(data[i].get('y'))
#                     y_pos_truck_noLC = list(data[i].get('bbox')[:, 1])
#                 else:
#                     print("vehicle class unknown")
#         lc_trajectory = {
#             "Car_yAccel_LC": y_accel_car_LC,
#             "Car_yAccel_noLC": y_accel_car_noLC,
#             "Truck_yAccel_LC": y_accel_truck_LC,
#             "Truck_yAccel_noLC": y_accel_truck_noLC,
#             "Car_ySpeed_LC": y_speed_car_LC,
#             "Car_ySpeed_noLC": y_speed_car_noLC,
#             "Truck_ySpeed_LC": y_speed_truck_LC,
#             "Truck_ySpeed_noLC": y_speed_truck_noLC,
#             "Car_yPos_LC": y_pos_car_LC,
#             "Car_yPos_noLC": y_pos_car_noLC,
#             "Truck_yPos_LC": y_pos_truck_LC,
#             "Truck_yPos_noLC": y_pos_truck_noLC
#         }
#         return lc_trajectory












# def filter_by_thw(tracks, 
#                   ego_type, preceding_type, 
#                   thw_lower_bound=0, thw_upper_bound=6, 
#                   min_duration=-1, 
#                   distance_threshold=100):
#     car_following_meta = {'ego_id': [], 'preceding_id': [], 'start_frame': [], 'end_frame': []}

#     all_ego_agent_id = set(tracks[tracks['class'] == ego_type]['id'].tolist())
#     all_preceding_agent_id = set(tracks[tracks['class'] == preceding_type]['id'].tolist())

#     frame_threshold = 25 * min_duration if min_duration != -1 else 2

#     for ego_id in all_ego_agent_id:
#         all_frames_with_agent = tracks[tracks['id'] == ego_id]
#         unique_preceding_agent_list = list((set(all_frames_with_agent['precedingId'].unique()) & all_preceding_agent_id) - {0})

#         for preceding_id in unique_preceding_agent_list:
#             vehicle_follow_frames = all_frames_with_agent[all_frames_with_agent['precedingId'] == preceding_id]
#             min_thw, max_thw = vehicle_follow_frames['thw'].min(), vehicle_follow_frames['thw'].max()

#             # Compute initial distance and velocity difference directly
#             initial_frame = vehicle_follow_frames['frame'].iloc[0]
#             ego_track = tracks[(tracks['id'] == ego_id) & (tracks['frame'] == initial_frame)].iloc[0]
#             preceding_track = tracks[(tracks['id'] == preceding_id) & (tracks['frame'] == initial_frame)].iloc[0]
#             distance = np.sqrt((ego_track['x'] - preceding_track['x']) ** 2 + (ego_track['y'] - preceding_track['y']) ** 2)
#             del_v = np.sqrt(ego_track['xVelocity'] ** 2 + ego_track['yVelocity'] ** 2) - np.sqrt(preceding_track['xVelocity'] ** 2 + preceding_track['yVelocity'] ** 2)

#             if thw_lower_bound <= min_thw <= thw_upper_bound and len(vehicle_follow_frames) >= frame_threshold and distance >= distance_threshold:
#                 car_following_meta['ego_id'].append(ego_id)
#                 car_following_meta['preceding_id'].append(preceding_id)
#                 car_following_meta['start_frame'].append(initial_frame)
#                 car_following_meta['end_frame'].append(vehicle_follow_frames['frame'].iloc[-1])

#     return car_following_meta


def filter_by_ttc(tracks, 
                  ego_type, preceding_type, 
                  ttc_lower_bound=0, ttc_upper_bound=6, 
                  min_duration=-1):
    car_following_meta = {'ego_id': [], 'preceding_id': [],
                          'start_frame': [], 'end_frame': []}

    # all_ego_agent_id = set(tracks[(tracks['class'] == ego_type) & (tracks['numLaneChanges'] == 0)]['id'].tolist())
    # all_preceding_agent_id = set(tracks[(tracks['class'] == preceding_type) & (tracks['numLaneChanges'] == 0)]['id'].tolist())

    all_ego_agent_id = set(tracks[tracks['class'] == ego_type]['id'].unique())
    all_preceding_agent_id = set(tracks[tracks['class'] == preceding_type]['id'].unique())
    frame_threshold = 25 * min_duration if min_duration != -1 else 2

    for ego_id in all_ego_agent_id:
        all_frames_with_agent = tracks[(tracks['id'] == ego_id)]
        unique_preceding_agent_list = list((set(all_frames_with_agent['precedingId'].unique()) & all_preceding_agent_id))

        for preceding_id in unique_preceding_agent_list:
            vehicle_follow_frames = all_frames_with_agent[all_frames_with_agent['precedingId'] == preceding_id]
            min_ttc, max_ttc = vehicle_follow_frames['ttc'].min(), vehicle_follow_frames['ttc'].max()
            if ttc_lower_bound < min_ttc <= ttc_upper_bound and len(vehicle_follow_frames) >= frame_threshold:
                car_following_meta['ego_id'].append(ego_id)
                car_following_meta['preceding_id'].append(preceding_id)
                car_following_meta['start_frame'].append(
                    vehicle_follow_frames['frame'].iloc[0])
                car_following_meta['end_frame'].append(
                    vehicle_follow_frames['frame'].iloc[-1])

    return car_following_meta

