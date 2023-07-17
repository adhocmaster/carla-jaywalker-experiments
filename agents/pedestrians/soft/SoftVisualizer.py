import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from agents.pedestrians.soft.LaneSection import LaneSection
from agents.pedestrians.soft.NavPath import NavPath
from matplotlib.patches import Rectangle, Circle
import matplotlib.patches as mpatches

from agents.pedestrians.soft.NavPoint import NavPoint


class SoftVisualizer:

    def __init__(self, meterToPixel=30, dpi=100) -> None:
        self.meterToPixel = meterToPixel
        self.dpi = dpi
        pass

    def setFigureSize(self, navPath: NavPath) -> Figure:
        nPoints = len(navPath.path)
        width = navPath.roadWidth * self.meterToPixel * nPoints
        height = navPath.roadLength * self.meterToPixel
        
        wIn = width / self.dpi
        hIn = height / self.dpi
        return plt.figure(figsize=(wIn, hIn), dpi=self.dpi)
        # return plt.figure(), width, height
    
    def addVehicle(self, ax: Axes, navPath: NavPath, yOffset: float = 0):
        # vW = self.toFigUnit(2)
        # vH = self.toFigUnit(4)
        vW = 2
        vH = 4
        # print(vW, vH)
        # ax.add_patch(Rectangle((0, 0), vW, vH, color='blue'))

        color = '#aaffaa'
        if yOffset > 0:
            color = '#55aa55'

        egoLaneWrtCenter = navPath.egoLaneWrtCenter
        assert egoLaneWrtCenter > 0
        laneOffset = navPath.nEgoOppositeDirectionLanes + navPath.egoLaneWrtCenter - 1
        x = laneOffset * navPath.laneWidth + (navPath.laneWidth - vW) / 2
        ax.add_patch(Rectangle((x, yOffset), vW, vH, color=color))



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
            self.addNavPoint(ax, navPath, i)

    def addNavPoint(self, ax: Axes, navPath: NavPath, idx: int, addVehicle=False):
        navPoint = navPath.path[idx]
        # if navPoint.isInFrontOfEgo():
        laneOffset = navPath.nEgoOppositeDirectionLanes + navPath.getPointLaneIdWrtCenter(navPoint) - 1
        x = laneOffset * navPath.laneWidth + (navPath.laneWidth) / 2
        if navPoint.laneSection == LaneSection.LEFT:
            x -= navPath.laneWidth / 2
        if navPoint.laneSection == LaneSection.RIGHT:
            x += navPath.laneWidth / 2

        circle = Circle((x, navPoint.distanceToInitialEgo), 0.5)
        ax.add_patch(circle)
        ax.text(x, navPoint.distanceToInitialEgo, f"{idx+1}", horizontalalignment='center', verticalalignment='center')

        
        if addVehicle:
            yOffset = navPoint.distanceToInitialEgo - navPoint.distanceToEgo
            self.addVehicle(ax, navPath, yOffset)

    def visualizeNavPath(self, navPath: NavPath):
        figure = self.setFigureSize(navPath)

        nPoints = len(navPath.path)

        for i, navPoint in enumerate(navPath.path):
            ax = figure.add_subplot(1, nPoints, i+1)
            ax.set_xlim(left=0, right=navPath.roadWidth)
            ax.set_ylim(bottom=0, top=navPath.roadLength)
            self.addVehicle(ax, navPath)
            self.addLaneMarkings(ax, navPath)
            self.addNavPoint(ax, navPath, i, addVehicle=True)

        # put the vehicle at the bottom

        
