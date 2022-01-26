import pytest

from lib import ActorManager

# @pytest.fixture
# def actorManager(client) -> ActorManager:
#     return ActorManager(client)

@pytest.mark.parametrize("client", ["circle_t_junctions"], indirect=True)
def test_stopSigns(client):
    actorManager = ActorManager(client)

    print(actorManager.getActorTypes())

    stopActors = actorManager.getTrafficStopSigns()
    print(stopActors)
    assert len(stopActors) > 0


@pytest.mark.parametrize("client", [None], indirect=True)
def test_TrafficDefaultMap(client):
    actorManager = ActorManager(client)

    print(actorManager.getActorTypes())

    stopActors = actorManager.getTrafficStopSigns()
    assert len(stopActors) > 0

