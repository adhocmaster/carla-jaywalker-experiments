import carla
import copy
import math

class Geometry: 

    @staticmethod
    def getGlobalYaw(subject: carla.Vector3D): 
        """Returns rotation around Z"""
        return math.atan2(subject.y, subject.x)

    
    @staticmethod
    def changeCartesianCenter(subject: carla.Vector3D, center: carla.Vector3D, centerDirection: carla.Vector3D=None, centerRotation=None) -> carla.Vector3D:

        clone = subject - center 
        # clone = carla.Vector3D(x=subject.x, y=subject.y, z=subject.z)
        # clone.x -= center.x
        # clone.y -= center.y
        # clone.z -= center.z

        if centerDirection is not None:
            angle = -Geometry.getGlobalYaw(centerDirection)
            clone = Geometry.rotateAroundZ(clone, angle)
        elif centerRotation is not None:
            angle = -centerRotation
            clone = Geometry.rotateAroundZ(clone, angle)


        return clone
    

    @staticmethod
    def rotateAroundZ(subject: carla.Vector3D, angle) -> carla.Vector3D:
        """_summary_

        Args:
            subject (carla.Vector3D): _description_
            angle (_type_): If we are transforming to another reference frame, angle should negated 

        Returns:
            carla.Vector3D: _description_
        """

        clone = carla.Vector3D(x=subject.x, y=subject.y, z=subject.z)
        clone.x = subject.x * math.cos(angle) - subject.y * math.sin(angle)
        clone.y = subject.x * math.sin(angle) + subject.y * math.cos(angle)
        
        return clone

    
