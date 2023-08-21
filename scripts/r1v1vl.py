exec(open("sys_path_hack.py").read())

import logging
import click

from research import ResearchFactory
from lib import MapNames, SimulationMode


@click.command()
@click.option(
    '--max_ticks',
    metavar='number',
    default=1000,
    type=int,
    help='Number of ticks the simulator will run'
    )
def r1v1m2Default(max_ticks):
    research = ResearchFactory.createResearch1v1NavPathModel(
        map=MapNames.varied_width_lanes, 
        defaultLogLevel=logging.WARN, 
        settingsId="setting1", 
        simulationMode = SimulationMode.SYNCHRONOUS,
        stats=False
         
    )
    research.maxStepsPerCrossing = max_ticks
    # research.run(maxTicks=max_ticks)
    research.reset()
    research.simulator.loop(maxTicks=max_ticks)


if __name__ == '__main__':
    r1v1m2Default()