


# @staticmethod
# def calculate_ttc(df):
    
#     # Extract required information from the DataFrame
#     x_lead = df['x'] - df['width']
#     x_follow = df['x']
#     lead_length = df['width']
#     v_lead = df['precedingXVelocity']
#     v_follow = df['xVelocity']

#     # Calculate the numerator and denominator of the TTC formula
#     numerator = x_lead - x_follow - lead_length
#     denominator = v_follow - v_lead

#     # Avoid division by zero by replacing zeros in the denominator with a small value
#     denominator = np.where(denominator == 0, 1e-9, denominator)

#     # Calculate TTC
#     ttc = numerator / denominator

#     return ttc


import numpy as np


            
        
