from typing import Tuple, Optional

import grpc
from Crypto.PublicKey import RSA

import ClientServerComms_pb2
import ClientServerComms_pb2_grpc
import grpc_channel
from utils import crypto
from utils.ip import *
from utils.crypto import *


def login(username: str, keypair: RSA.RsaKey, challenge_nonce: int, preferred_ip: Optional[str] = None):
    assert keypair.has_private, 'Keypair must contain a private key'

    local_ips = get_local_ipv4_addresses()
    chosen_ip = local_ips[0]
    if preferred_ip is not None:
        assert preferred_ip in local_ips or preferred_ip.startswith('127.')
        chosen_ip = preferred_ip

    with grpc_channel.create_channel() as channel:
        stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)

        # Create the digital signature
        signature_data = ";".join((username, chosen_ip)).encode('utf-8')
        digital_signature = create_signature(signature_data, keypair)
        sig = ClientServerComms_pb2.DigitalSignature(
            username=username,
            signature=digital_signature
        )

        # Create the login request
        login_request = ClientServerComms_pb2.LoginRequest(
            username=username,
            address=ipv4_to_fixed32(chosen_ip),
            digitalSignature=sig,
            challenge_nonce=challenge_nonce
        )

        # Make the gRPC call
        try:
            response = stub.Login(login_request)
            # Handle response
        except grpc.RpcError as e:
            print(e)


def register(username: str) -> Tuple[str, RSA.RsaKey, RSA.RsaKey]:
    keypair_login: RSA.RsaKey = generate_rsa_keypair()
    keypair_chat: RSA.RsaKey = generate_rsa_keypair()
    with grpc_channel.create_channel() as channel:
        stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
        response: ClientServerComms_pb2.SignUpResponse = stub.SignUp(
            ClientServerComms_pb2.SignUpRequest(username=username,
                                                publicKeyLogin=keypair_login.public_key().export_key(format='DER'),
                                                publicKeyChat=keypair_chat.public_key().export_key(format='DER')))
        challenge = int.from_bytes(decrypt_ciphertext(response.challenge, keypair_login), byteorder='little')
        response = challenge - 1
        response_signature = create_signature(response.to_bytes(64 // 8, byteorder='little'), keypair_login)
        stub.SignUpChallengeResponse(ClientServerComms_pb2.SignUpChallengeResponseRequest(
            challenge_response=response_signature))
    return username, keypair_login, keypair_chat
