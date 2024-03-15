import base64
import json
from typing import Tuple

from Crypto.PublicKey import RSA


def open_key_from_bytes(key: bytes) -> RSA.RsaKey:
    raise NotImplemented


def login(username: str, keypair: RSA.RsaKey):
    assert keypair.has_private, 'Keypair must contain a private key'
    raise NotImplemented


def register(username: str) -> Tuple[str, RSA.RsaKey]:
    raise NotImplemented


def parse_account_file(account_file: str) -> Tuple[str, RSA.RsaKey]:
    j = json.loads(account_file)

    assert 'username' in j, 'Account file must contain the username'
    assert 'keypair' in j, 'Account file must contain keypair'

    keypair = open_key_from_bytes(base64.b64decode(j['keypair'].encode('utf-8')))
    assert keypair.has_private, 'Keypair must contain a private key'

    return j['username'], keypair


def export_account_file(username: str, keypair: RSA.RsaKey) -> str:
    assert keypair.has_private, 'Keypair must contain a private key'

    return json.dumps({
        'username': username,
        'keypair': base64.b64encode(keypair.exportKey()).decode('utf-8')
    })
