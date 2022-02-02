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
        self.dict = self.createFactorDict(defaultFactorFile)
        
        pass
        
    def createFactorDict(defaultFactorFile:str) -> Dict[str, any]:
        dict = None
        with open(defaultFactorFile, "r") as stream:
            dict = yaml.safe_load(defaultFactorFile)
        if dict is None:
            raise Exception(f"No config found in {defaultFactorFile}")
        return dict

    def __setattr__(self, __name: str, __value: any) -> None:
        self.dict[__name] = __value
        pass


    def __getattr__(self, __name: str):
        if __name in self.dict:
            return self.dict[__name]
        raise UndefinedProperty("InternalFactors do not have {__name}")