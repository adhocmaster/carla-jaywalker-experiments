import click
from research import ResearchFactory
from lib import MapNames

@click.command()
@click.option(
    '--max_ticks',
    metavar='number',
    default=1000,
    type=int,
    help='Number of ticks the simulator will run'
    )
def r1v1m2Default(max_ticks):
    research = ResearchFactory.createResearch1v1(map=MapNames.Town02_Opt)
    research.run(maxTicks=max_ticks)


if __name__ == '__main__':
    r1v1m2Default()