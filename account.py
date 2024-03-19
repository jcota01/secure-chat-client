from typing import Tuple, Optional

from Crypto.PublicKey import RSA

import ClientServerComms_pb2
import ClientServerComms_pb2_grpc
import grpc_channel
from utils.ip import *
from utils.crypto import *


def login(username: str, keypair: RSA.RsaKey, preferred_ip: Optional[str] = None) -> bool:
    assert keypair.has_private, 'Keypair must contain a private key'

    local_ips = get_local_ipv4_addresses()
    chosen_ip = local_ips[0]
    if preferred_ip is not None:
        assert preferred_ip in local_ips
        chosen_ip = preferred_ip

    with grpc_channel.create_channel() as channel:
        stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
        response: ClientServerComms_pb2.LoginResponse = stub.Login(
            ClientServerComms_pb2.LoginRequest(username=username,
                                               address=ipv4_to_fixed32(chosen_ip),
                                               digitalSignature=create_signature(
                                                   ";".join((username, chosen_ip)).encode('utf-8'),
                                                   keypair
                                               )))
        return response


def register(username: str) -> Tuple[str, RSA.RsaKey]:
    keypair_login = generate_rsa_keypair()
    keypair_chat = generate_rsa_keypair()
    with grpc_channel.create_channel() as channel:
        stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
        response: ClientServerComms_pb2.SignUpResponse = stub.Login(
            ClientServerComms_pb2.SignUpRequest(username=username,
                                               publicKeyLogin=keypair_login.public_key(),
                                                publicKeyChat=keypair_chat.public_key()
                                                ))
        return response
