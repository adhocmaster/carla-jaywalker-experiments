exec(open("sys_path_hack.py").read())

import logging
import click

from research import ResearchFactory
from lib import MapNames, SimulationMode
import time


@click.command()
@click.option(
    '--max_ticks',
    metavar='number',
    default=500,
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
    default="psi-0048",
    type=str,
    help='NavPath Scenario'
    )
@click.option(
    '-e', '--episodes',
    metavar='int',
    default=1,
    type=int,
    help='Number of episodes to run'
    )
@click.option(
    '-seed', '--seed',
    metavar='int',
    default=39,
    type=int,
    help='random seed'
    )
def rNv1Default(max_ticks, stats, record, scenario, episodes, seed):
    research = ResearchFactory.createResearchNv1NavPathModel(
        map=MapNames.varied_width_lanes, 
        defaultLogLevel=logging.WARN, 
        settingsId="setting1-ego-lc-right-psi-0002", 
        # settingsId="setting1-ego-rightmost-psi-0002", 
        simulationMode = SimulationMode.SYNCHRONOUS,
        stats=stats,
        ignoreStatsSteps=100,
        record=record,
        scenario=scenario
         
    )
    research.maxStepsPerCrossing = max_ticks
    # research.run(maxTicks=max_ticks)
    for i in range(episodes):
        try:
            research.reset(seed + i)
        except Exception as e:
            print(f"Failed to reset episode {i} with seed {seed + i}")
            print(e)
            continue
        research.simulator.loop(maxTicks=max_ticks)
    # time.sleep(10)
    research.onEnd() # make sure to call this to save stats


if __name__ == '__main__':
    rNv1Default()