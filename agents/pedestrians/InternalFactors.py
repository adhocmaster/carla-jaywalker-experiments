from lib import UndefinedProperty

class InternalFactors:
    """
        Internal factors that affect different models
    """

    def __init__(self) -> None:
        self.dict = {
            "relaxation_time": 2, 
            "desired_speed": 2,
            "desired_gap": 2
        }
        pass

    def __setattr__(self, __name: str, __value: any) -> None:
        self.dict[__name] = __value
        pass


    def __getattr__(self, __name: str):
        if __name in self.dict:
            return self.dict[__name]
        raise UndefinedProperty("InternalFactors do not have {__name}")