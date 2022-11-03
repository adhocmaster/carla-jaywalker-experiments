import carla

class CrosswalkModel:

    def createGoalLine(self, length):
        goal = self.idealDestination
        #goalLine = shapely.LineString([goal.coords[0]-length, goal.coords[0]+length])
        #self.goalLine = goalLine
        # TODO: muktadir createGoalLine
        raise NotImplementedError("createGoalLine is not implemented")

    
    def getNextDestinationPoint(self, agentLocation: carla.Location):
        # TODO
        # find if the pedestrian reached the local y coordinate with a threshold around 100 cm
        # change next destination point to the next intermediate point return 

        if self.hasReachedNextDestinationPoint(agentLocation):
            if self.nextIntermediatePointIdx == len(self.intermediatePoints) - 1:
                return self.finalDestination
            self.nextIntermediatePoint += 1 # this might overflow if we have reached the final 
        
        return self.intermediatePoints[self.nextIntermediatePointIdx]

    
    def hasReachedNextDestinationPoint(self, agentLocation: carla.Location):
        # TODO: fill it out
        return False

        
    pass