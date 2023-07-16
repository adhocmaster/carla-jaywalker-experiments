import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.NavPath import NavPath
from matplotlib.patches import Rectangle, Circle
import matplotlib.patches as mpatches


class SoftVisualizer:

    def __init__(self, meterToPixel=30, dpi=100) -> None:
        self.meterToPixel = meterToPixel
        self.dpi = dpi
        pass

    def setFigureSize(self, navPath: NavPath) -> Figure:
        width = navPath.roadWidth * self.meterToPixel
        height = navPath.roadLength * self.meterToPixel
        
        wIn = width / self.dpi
        hIn = height / self.dpi
        return plt.figure(figsize=(wIn, hIn), dpi=self.dpi)
        # return plt.figure(), width, height
    
    def addVehicle(self, ax: Axes, navPath: NavPath):
        # vW = self.toFigUnit(2)
        # vH = self.toFigUnit(4)
        vW = 2
        vH = 4
        # print(vW, vH)
        # ax.add_patch(Rectangle((0, 0), vW, vH, color='blue'))
        egoLaneWrtCenter = navPath.egoLaneWrtCenter
        assert egoLaneWrtCenter > 0
        laneOffset = navPath.nEgoOppositeDirectionLanes + navPath.egoLaneWrtCenter - 1
        x = laneOffset * navPath.laneWidth + (navPath.laneWidth - vW) / 2
        ax.add_patch(Rectangle((x, 0), vW, vH, color='green'))
        # arrow = mpatches.FancyArrowPatch((x + vW/2, vH), (x + vW/2, vH+2),
        #                          mutation_scale=40)
        # ax.add_patch(arrow)



    # def toFigUnit(self, meters: float) -> float:
    #     px = 3 * self.meterToPixel
    #     return px / self.dpi

    def addLaneMarkings(self, ax: Axes, navPath: NavPath):
        # we put ego lanes on the right and opposite direction lanes on the left
        for i in range(navPath.nLanes):
            ax.vlines(i * navPath.laneWidth, 0, 100, color='black', linewidth=1)
        
        for i in range(navPath.nEgoOppositeDirectionLanes):
            x = (i+1) * navPath.laneWidth - navPath.laneWidth / 2
            arrow = mpatches.FancyArrowPatch((x , 2), (x, 0),
                                    mutation_scale=40, color="C1")
            ax.add_patch(arrow)

        for i in range(navPath.nEgoDirectionLanes):
            x = (i + 1 + navPath.nEgoOppositeDirectionLanes) * navPath.laneWidth - navPath.laneWidth / 2
            arrow = mpatches.FancyArrowPatch((x , 0), (x, 2),
                                    mutation_scale=40, color="C2")
            ax.add_patch(arrow)


    def addNavPoints(self, ax: Axes, navPath: NavPath):
        for i, navPoint in enumerate(navPath.path):
            if navPoint.isInFrontOfEgo():
                laneOffset = navPath.nEgoOppositeDirectionLanes + navPath.getPointLaneIdWrtCenter(navPoint) - 1
                x = laneOffset * navPath.laneWidth + (navPath.laneWidth) / 2
                if navPoint.laneSection == LaneSection.LEFT:
                    x -= navPath.laneWidth / 2
                if navPoint.laneSection == LaneSection.RIGHT:
                    x += navPath.laneWidth / 2

                circle = Circle((x, navPoint.distanceToInitialEgo), 0.5)
                ax.add_patch(circle)
                ax.text(x, navPoint.distanceToInitialEgo, f"{i+1}", horizontalalignment='center', verticalalignment='center')

    def visualizeNavPath(self, navPath: NavPath):
        figure = self.setFigureSize(navPath)

        ax = figure.add_subplot(111)
        ax.set_xlim(left=0, right=navPath.roadWidth)
        ax.set_ylim(bottom=0, top=navPath.roadLength)
        self.addVehicle(ax, navPath)
        self.addLaneMarkings(ax, navPath)
        self.addNavPoints(ax, navPath)

        # put the vehicle at the bottom

        
