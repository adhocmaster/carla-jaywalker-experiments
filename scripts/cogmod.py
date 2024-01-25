exec(open("sys_path_hack.py").read())

import click
from research import ResearchFactory, SimulationMode

@click.command()
@click.option(        
    '--max_ticks',
    metavar='number',
    default=2000,
    type=int,
    help='Number of ticks the simulator will run'
    )
def ResearchCogMod(max_ticks):
    research = ResearchFactory.createResearchCogMod(maxTicks=max_ticks, 
                                                    simulationMode=SimulationMode.SYNCHRONOUS, 
                                                    simulation_id='setting1')


if __name__ == '__main__':
    ResearchCogMod()