from typing import List
from dataclasses import dataclass, field
from .NavPath import NavPath

@dataclass
class GroupOrdering:
    step: int
    groupOrdering: List[int]

class GroupNavPath:

    """Group NavPath has multiple pedestrians and they are short-lived. A pedestrian in their crossing lifespan can be either controlled by a Group Nav Path or a Nav Path. 
       The role of this class is to adjust individual nav paths based on group formation and span
    """

    def __init__(
            navPaths: List[NavPath],
            groupOrderings: List[GroupOrdering]
            
        ):
        
        self.navPaths = navPaths
        self.groupOrderings = groupOrderings
