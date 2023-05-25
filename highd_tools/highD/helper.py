import pandas as pd
from scipy import stats


def calculate_ttc(dataframe):
    
    df = dataframe.copy()
    # Set default TTC values to zero
    df['calculated_ttc'] = 0

    # Find rows with preceding vehicles
    has_preceding = df['precedingId'] != 0

    # Find ego front location
    df.loc[has_preceding, 'ego_front_location'] = df.loc[has_preceding, 'x'] + (df.loc[has_preceding, 'xVelocity'] < 0) * df.loc[has_preceding, 'width']

    # Merge DataFrame with itself on 'precedingId' and 'frame' to get preceding vehicle information
    df = df.merge(df[['id', 'frame', 'x', 'width']], how='left', left_on=['precedingId', 'frame'], right_on=['id', 'frame'], suffixes=('', '_preceding'))

    # Find preceding rear location
    df.loc[has_preceding, 'preceding_rear_location'] = df.loc[has_preceding, 'x_preceding'] + df.loc[has_preceding, 'width_preceding']

    # Calculate TTC for rows with preceding vehicles
    df.loc[has_preceding, 'calculated_ttc'] = (df.loc[has_preceding, 'preceding_rear_location'] - df.loc[has_preceding, 'ego_front_location']) / (df.loc[has_preceding, 'xVelocity'] - df.loc[has_preceding, 'precedingXVelocity'])

    # clip negative values to zero
    df.loc[df['calculated_ttc'] < 0, 'calculated_ttc'] = 0

    # Drop unnecessary columns
    df.drop(columns=['ego_front_location', 'id_preceding', 'x_preceding', 'width_preceding', 'preceding_rear_location'], inplace=True)

    print('returning with calculated TTC as a new column. Values follow same trend but not exact')
    return df



def ks_test_ttc(data: pd.DataFrame) -> float:
    """
    Compute the Kolmogorov-Smirnov test between 'ttc' and 'calculated_ttc' columns in the DataFrame.

    :param data: DataFrame with columns 'ttc' and 'calculated_ttc'.
    :return: KS test statistic
    """
    # Extract 'ttc' and 'calculated_ttc' columns from the DataFrame
    ttc = data['ttc']
    calculated_ttc = data['calculated_ttc']
    
    # Compute the KS test
    ks_statistic, p_value = stats.ks_2samp(ttc, calculated_ttc)
    
    return ks_statistic, p_value



def get_scenario_data(dfs, follow_meta_df, scenario_id):
    # Retrieve scenario data
    scenario_df = follow_meta_df.iloc[scenario_id]

    dataset_id = scenario_df['dataset_id']
    ego_id = scenario_df['ego_id']
    prec_id = scenario_df['preceding_id']
    start_frame = scenario_df['start_frame']
    end_frame = scenario_df['end_frame']
    
    df = dfs[int(dataset_id)-1]
    ego_df = df[(df['id'] == ego_id) & (df['frame'].between(start_frame, end_frame))]
    prec_df = df[(df['id'] == prec_id) & (df['frame'].between(start_frame, end_frame))]

    return ego_df, prec_df
