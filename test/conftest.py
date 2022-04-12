
import pytest
import carla

@pytest.fixture
def client(request):   

    map = request.param
    print(map)

    client = carla.Client("127.0.0.1", 2000)

    if map is not None:
        client.load_world(map)

    return client

@pytest.fixture
def host():
    return "127.0.0.1"

@pytest.fixture
def port():
    return 2000