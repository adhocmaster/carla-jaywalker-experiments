from enum import Enum
from typing import List, Union, Tuple
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
        navPaths = []
        for pathDic in pathsDics:
            navPaths.extend(NavObjectMapper.pathFromDict(pathDic))
        return navPaths

    @staticmethod
    def pathFromDict(pathDic) -> List[NavPath]:
        """_summary_

        Args:
            pathDic (_type_): dictionary for a single NavPath
        """
        # print(pathDic['roadConfiguration'])
        roadConfiguration = from_dict(data_class=NavPathRoadConfiguration, data=pathDic['roadConfiguration'])
        # print(pathDic['egoConfiguration'])
        egoConfiguration = from_dict(data_class=NavPathEgoConfiguration, data=pathDic['egoConfiguration'])
        # print(pathDic['pedConfiguration'])

        # branch if it's a group or individual
        navPaths = []
        if "pedestrians" in pathDic:
            for idx, pedDic in enumerate(pathDic['pedestrians']):
                pedConfiguration, path = NavObjectMapper.extractPedestrian(pedDic)
                navPaths.append(NavPath(
                    id = f"{pathDic['id']}-{idx}",
                    groupId = pathDic['id'],
                    roadConfiguration=roadConfiguration,
                    egoConfiguration=egoConfiguration,
                    pedConfiguration=pedConfiguration,
                    path=path
                ))
        else:
            pedConfiguration, path = NavObjectMapper.extractPedestrian(pathDic)
            navPaths.append(NavPath(
                id = pathDic['id'],
                groupId = None,
                roadConfiguration=roadConfiguration,
                egoConfiguration=egoConfiguration,
                pedConfiguration=pedConfiguration,
                path=path
            ))
        
        # print(navPaths)
        return navPaths
    
    @staticmethod
    def extractPedestrian(pedDic) -> Tuple[NavPathPedestrianConfiguration, List[NavPoint]]:
        """_summary_

        Args:
            pedDic (_type_): dictionary for a single pedestrian
        """
        pedConfiguration = from_dict(data_class=NavPathPedestrianConfiguration, data=pedDic['pedConfiguration'], config=Config(cast=[Enum]))
        path = [NavObjectMapper.pointFromDict(pointDic) for pointDic in pedDic['path']]

        return (pedConfiguration, path)
    
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

