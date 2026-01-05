"""Starts a network server with user-space transforms registered."""
from gsp_network.tools.network_server import ServerSample


# =============================================================================
# import all user-space transform
# - thus they get registered in the TransformRegistry
# =============================================================================
from transform_load import TransformLoad


if __name__ == "__main__":
    print("Starting the network server with all the user-space transforms...")
    server = ServerSample()
    server.run()
