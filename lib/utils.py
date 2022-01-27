import carla
class Utils:
    @staticmethod
    def createClient(logger, host, port, timeout=5.0):
        client = carla.Client(host, port)
        client.set_timeout(timeout)

        logger.info(f"Client carla version: {client.get_client_version()}")
        logger.info(f"Server carla version: {client.get_server_version()}")

        if client.get_client_version() != client.get_server_version():
            logger.warning("Client and server version mistmatch. May not work properly.")

        return client
