import grpc

"""
Creates a GRPC channel to the server. We do this in a function so we can decide later how to specify the server
address.
"""


def create_channel():
    return grpc.insecure_channel("127.0.0.1:6000")
