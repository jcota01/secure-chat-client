from typing import Tuple

from Crypto.PublicKey import RSA


def login(username: str, keypair: RSA.RsaKey):
    assert keypair.has_private, 'Keypair must contain a private key'
    raise NotImplemented


def register(username: str) -> Tuple[str, RSA.RsaKey]:
    raise NotImplemented
