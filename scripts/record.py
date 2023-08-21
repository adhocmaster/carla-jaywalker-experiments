exec(open("sys_path_hack.py").read())

import logging
import click
import carla

from research import ResearchFactory
from lib import MapNames, SimulationMode


@click.command()
@click.option(
    '-h', '--host',
    metavar='str',
    default="127.0.0.1",
    type=str,
    help='Host'
    )
@click.option(
    '-p', 'port',
    metavar='number',
    default=2000,
    type=int,
    help='Port'
    )
@click.option(
    '-t', '--duration',
    metavar='number',
    default=1000,
    type=int,
    help='Duration in seconds'
    )

@click.option(
    '-r', '--record',
    metavar='boolean',
    default=False,
    type=bool,
    help='Start recording'
    )

@click.option(
    '-p', '--play',
    metavar='boolean',
    default=False,
    type=bool,
    help='Start recording'
    )
@click.option(
    '-a', '--actor',
    metavar='str',
    default=None,
    type=str,
    help='Actor to follow while playing'
    )
@click.option(
    '-f', '--file',
    metavar='str',
    default=None,
    type=str,
    help='File to play'
    )
    

def main(host, port, duration, record, play, actor, file):
    
    try:

        client = carla.Client(host, port)
        client.set_timeout(2.0)
        world = client.get_world()
    


if __name__ == '__main__':
    main()