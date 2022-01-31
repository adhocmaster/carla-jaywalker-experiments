import click
from research import ResearchFactory

@click.command()
@click.option(
    '--max_ticks',
    metavar='number',
    default=100,
    type=int,
    help='Number of ticks the simulator will run'
    )
def r1v1Default(max_ticks):
    research = ResearchFactory.createResearch1v1(maxTicks=max_ticks)


if __name__ == '__main__':
    r1v1Default()