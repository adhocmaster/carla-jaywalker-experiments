from dataclasses import dataclass
import carla

from agents.pedestrians.PedestrianAgent import PedestrianAgent
from settings.SourceDestinationPair import SourceDestinationPair

@dataclass
class WalkerActor:
    carlaActor: carla.Actor
    agent: PedestrianAgent
    settings: SourceDestinationPair
    