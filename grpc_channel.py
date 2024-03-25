import os
import socket
from typing import Optional

import grpc

"""
Creates a GRPC channel to the server. We do this in a function so we can decide later how to specify the server
address.
"""


def create_channel(src_address: Optional[str] = None):
    return SocketChannel('127.0.0.1', 6000, src_address or os.environ.get('BIND_IP'))


class SocketChannel:
    """
    gRPC doesn't directly support us choosing our client IP. This class uses a slightly hacky method to support it.

    If our machine has multiple NICs, or we are using an IP on the 127.x.x.x range for testing, we need to make sure
    we connect from the right source IP or the server will route our messages back to the wrong place.

    If we had more time, a better solution would be for the client to specify its IP on login and for the server to do
    a challenge-response to that IP over HTTP to prove control. But this works for now (until the gRPC lib changes).
    """
    def __init__(self, server_address: str, server_port: int, src_address: Optional[str] = None):
        self.server_address: str = server_address
        self.server_port: int = server_port
        self.src_address: Optional[str] = src_address
        self._socket = None
        self._channel = None

    def __enter__(self):
        if self.src_address is not None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((self.src_address, 0))  # Use port 0 for ephemeral port selection
            self._socket.connect((self.server_address, self.server_port))
            self._channel = grpc.insecure_channel('{}:{}'.format(self.server_address, self.server_port),
                                                  options=(('grpc.so_reuseport', 0),), _sock=self._socket)
        else:
            self._channel = grpc.insecure_channel('{}:{}'.format(self.server_address, self.server_port),
                                                  options=(('grpc.so_reuseport', 0),))
        return self._channel

    def __exit__(self, exc_type, exc_value, traceback):
        if self._channel is not None:
            self._channel.close()
        if self._socket is not None:
            self._socket.close()
