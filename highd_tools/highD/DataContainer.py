from dataclasses import dataclass
from numpy import ndarray
from pandas import DataFrame


@dataclass
class DataContainer:

    id : int

    image : ndarray
    recordingMeta : DataFrame
    tracksMeta : DataFrame
    tracks : DataFrame

    recordingMeta_dict : dict
    tracksMeta_dict : dict
    tracks_dict : dict

