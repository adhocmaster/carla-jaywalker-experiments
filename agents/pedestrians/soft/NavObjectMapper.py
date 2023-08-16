from enum import Enum
from typing import List
from dacite import from_dict, Config

from agents.pedestrians.soft.NavPath import NavPath, NavPathPedestrianConfiguration, NavPathRoadConfiguration, NavPathEgoConfiguration
from agents.pedestrians.soft.NavPoint import NavPoint, NavPointBehavior, NavPointLocation

class NavObjectMapper:

    @staticmethod
    def pathsFromDicts(pathsDics) -> List[NavPath]:
        """_summary_

        Args:
            pathsDics (_type_): a list of NavPaths in dictionary form
        """
        return [NavObjectMapper.pathFromDict(pathDic) for pathDic in pathsDics]

    @staticmethod
    def pathFromDict(pathDic) -> NavPath:
        """_summary_

        Args:
            pathDic (_type_): dictionary for a single NavPath
        """
        # print(pathDic['roadConfiguration'])
        roadConfiguration = from_dict(data_class=NavPathRoadConfiguration, data=pathDic['roadConfiguration'])
        # print(pathDic['egoConfiguration'])
        egoConfiguration = from_dict(data_class=NavPathEgoConfiguration, data=pathDic['egoConfiguration'])
        # print(pathDic['pedConfiguration'])
        pedConfiguration = from_dict(data_class=NavPathPedestrianConfiguration, data=pathDic['pedConfiguration'], config=Config(cast=[Enum]))
        path = [NavObjectMapper.pointFromDict(pointDic) for pointDic in pathDic['path']]

        return NavPath(
            id = pathDic['id'],
            roadConfiguration=roadConfiguration,
            egoConfiguration=egoConfiguration,
            pedConfiguration=pedConfiguration,
            path=path
        )
    
    @staticmethod
    def pointFromDict(pointDic) -> NavPoint:
        """_summary_

        Args:
            pointDic (_type_): dictionary for a single NavPoint
        """
        location = from_dict(data_class=NavPointLocation, data=pointDic['location'], config=Config(cast=[Enum]))
        behavior = from_dict(data_class=NavPointBehavior, data=pointDic['behavior'])

        # print(id(behavior), id(behavior.behaviorTags))

        return NavPoint(
            location=location,
            behavior=behavior
        )

