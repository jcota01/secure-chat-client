import os
import socket
from typing import Optional

import grpc

"""
Creates a GRPC channel to the server. We do this in a function so we can decide later how to specify the server
address.
"""


def create_channel():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ca-cert.pem'), 'rb') as f:
        ca_cert = f.read()
    return grpc.secure_channel('127.0.0.1:6000', grpc.ssl_channel_credentials(root_certificates=ca_cert))
