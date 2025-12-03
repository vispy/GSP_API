from gsp_network.tools.network_server import ServerSample


# =============================================================================
# import all user-space transform
# - thus they get registered in the TransformRegistry
# =============================================================================
from gsp_extra.transform_links import TransformLoad


if __name__ == "__main__":
    print("Starting the network server with all the user-space transforms...")
    server = ServerSample()
    server.run()
