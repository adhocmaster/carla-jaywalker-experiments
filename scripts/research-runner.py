
exec(open("sys_path_hack.py").read())
from pydoc import cli
import click
import os
from lib import LoggerFactory, Utils
from research import Research1v1

from research import ResearchFactory


@click.group()
def chooseResearch():
    pass

@chooseResearch.command()
@click.option(
    '-h', '--host',
    metavar='ip address',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)',
    prompt=True
    )
@click.option(
    '-p', '--port',
    metavar='number',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 2000)', 
    prompt=True
    )
@click.option(
    '--log',
    metavar='DEBUG|INFO|WARNING|ERROR',
    default="INFO",
    help='Log level (default: INFO)', 
    prompt=True
    )
@click.option(
    '--output_dir',
    metavar='path',
    default="logs",
    help='Output directory (default logs)', 
    prompt=True
    )
@click.option(
    '--max_ticks',
    metavar='number',
    default=100,
    type=int,
    help='Number of ticks the simulator will run',
    prompt=True
    )
def r1v1(host, port, log, output_dir, max_ticks):
    # sample command: python research-runner.py r1v1 -h 127.0.0.1 -p 2000 --log INFO --output_dir logs
    # sample command: python research-runner.py r1v1 --host 127.0.0.1 --port 2000 --log INFO --output_dir logs
    click.echo(f"research chosen : R1v1 with host: {host}, port: {port}, log level: {log}, output directory: {output_dir}")
    
    # name = "Research1v1"
    # logPath = os.path.join(output_dir, f"{name}.log")
    # logger = LoggerFactory.getBaseLogger(name, defaultLevel=log, file=logPath)
    # client = Utils.createClient(logger, host, port)
    # research = Research1v1(client, log, output_dir)
    # research.run(maxTicks=100)

    
    research = ResearchFactory.createResearch1v1(host=host, port=port, defaultLogLevel=log, output_dir=output_dir)
    research.run(maxTicks=max_ticks)



    




if __name__ == '__main__':
    chooseResearch()