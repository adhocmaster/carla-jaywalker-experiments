from lib import UndefinedProperty
from typing import Dict
import yaml

class InternalFactors:
    """
        Internal factors that affect different models
    """

    def __init__(self, defaultFactorFile:str) -> None:
        # self.dict = {
        #     "relaxation_time": 0.1, 
        #     "desired_speed": 2,
        #     "desired_distance_gap": 2,
        #     "desired_time_gap": 2,
            
        # }
        self.__dict__["props"] = self._createFactorDict(defaultFactorFile)

        pass
        
    def _createFactorDict(self, defaultFactorFile:str) -> Dict[str, any]:
        dict = None
        with open(defaultFactorFile, "r") as stream:
            dict = yaml.safe_load(stream)
        if dict is None:
            raise Exception(f"No config found in {defaultFactorFile}")
        # print("parsed dict", dict)
        return dict

    def __contains__(self, name):
        if name in self.props:
            return True
        return False

    def __getitem__(self, name):
        if name in self.props:
            return self.props[name]
        raise UndefinedProperty(f"InternalFactors do not have {name}")

    def __setattr__(self, name: str, value: any) -> None:
        self.props[name] = value
        pass


    def __getattr__(self, name: str):
        return self[name]