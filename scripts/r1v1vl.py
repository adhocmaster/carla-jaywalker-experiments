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
@click.option(
    '--stats',
    metavar='boolean',
    default=False,
    type=bool,
    help='Collect stats'
    )
@click.option(
    '-r', '--record',
    metavar='boolean',
    default=False,
    type=bool,
    help='Collect stats'
    )
@click.option(
    '-s', '--scenario',
    metavar='string',
    default="psi-0002",
    type=str,
    help='NavPath Scenario'
    )
def r1v1m2Default(max_ticks, stats, record, scenario):
    research = ResearchFactory.createResearch1v1NavPathModel(
        map=MapNames.varied_width_lanes, 
        defaultLogLevel=logging.WARN, 
        settingsId="setting1-ego-rightmost", 
        simulationMode = SimulationMode.SYNCHRONOUS,
        stats=stats,
        record=record,
        scenario=scenario
         
    )
    research.maxStepsPerCrossing = max_ticks
    # research.run(maxTicks=max_ticks)
    research.reset()
    research.simulator.loop(maxTicks=max_ticks)


if __name__ == '__main__':
    r1v1m2Default()