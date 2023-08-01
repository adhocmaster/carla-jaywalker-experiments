import argparse
import pandas as pd
import numpy as np

def calculate_angle(df):
    # Calculate difference between current and previous x and y
    df['diff_x'] = df['x'].diff()
    df['diff_y'] = df['y'].diff()

    # Calculate angle in radians
    df['angle_rad'] = np.arctan2(df['diff_y'], df['diff_x'])

    # Convert radians to degrees
    df['angle_deg'] = np.degrees(df['angle_rad'])

    # Adjust angles to be more intuitive
    df['angle_deg'] = df['angle_deg'].apply(adjust_angle)

    # We don't need the temporary diff_x and diff_y columns anymore
    df = df.drop(columns=['diff_x', 'diff_y', 'angle_rad'])

    # Fill in any NaN values (these will be in the first row, where there's no previous frame to compare to)
    df['angle_deg'] = df['angle_deg'].fillna(0)

    return df

def adjust_angle(angle):
    if angle > 90:
        return angle - 180
    elif angle < -90:
        return angle + 180
    else:
        return angle

def main(input_filepath, output_filepath):
    # Load the CSV data
    df = pd.read_csv(input_filepath)

    # We want to calculate angles per vehicle, so we'll group by vehicle ID
    # Then we'll apply our angle calculation function to each group
    df = df.groupby('id').apply(calculate_angle)

    # Save the updated dataframe to a new CSV file
    df.to_csv(output_filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate vehicle angles from tracking data.')
    parser.add_argument('--input', '-i', type=str, required=True, help='Path to the input CSV file.')
    parser.add_argument('--output', '-o', type=str, required=True, help='Path to the output CSV file.')
    args = parser.parse_args()

    main(args.input, args.output)
