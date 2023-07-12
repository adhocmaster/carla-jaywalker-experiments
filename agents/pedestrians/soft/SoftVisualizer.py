import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from agents.pedestrians.soft.NavPath import NavPath
from matplotlib.patches import Rectangle


class SoftVisualizer:

    def __init__(self, meterToPixel=30, dpi=100) -> None:
        self.meterToPixel = meterToPixel
        self.dpi = dpi
        pass

    def setFigureSize(self, navPath: NavPath) -> Figure:
        width = navPath.roadWidth * self.meterToPixel
        maxDistanceToEgo = 0
        for navPoint in navPath.path:
            maxDistanceToEgo = max(maxDistanceToEgo, navPoint.distanceToEgo)
        height = maxDistanceToEgo * 2 * self.meterToPixel
        print(width / self.dpi, height / self.dpi)
        # return plt.figure(figsize=(width / self.dpi, height / self.dpi), dpi=self.dpi)
        return plt.figure()
    
    def addVehicle(self, ax: Axes):
        vW = self.toFigUnit(2)
        vH = self.toFigUnit(4)
        print(vW, vH)
        ax.add_patch(Rectangle((0, 0), vW, vH, color='blue'))

    def toFigUnit(self, meters: float) -> float:
        px = 3 * self.meterToPixel
        return px / self.dpi


    def visualizeNavPath(self, navPath: NavPath):
        figure = self.setFigureSize(navPath)
        ax = figure.add_subplot(111)
        ax.set_xlim(left=0, right=5)
        ax.set_ylim(bottom=0, top=5)
        self.addVehicle(ax)

        # put the vehicle at the bottom

        
