import base64
import json
from typing import Tuple

from Crypto.PublicKey import RSA

from utils.crypto import open_key_from_bytes


def parse_account_file(account_file: str) -> Tuple[str, RSA.RsaKey, RSA.RsaKey]:
    j = json.loads(account_file)

    assert 'username' in j, 'Account file must contain the username'
    assert 'keypair_login' in j, 'Account file must contain login keypair'
    assert 'keypair_chat' in j, 'Account file must contain chat keypair'

    keypair_login = open_key_from_bytes(base64.b64decode(j['keypair_login'].encode('utf-8')))
    assert keypair_login.has_private, 'Login keypair must contain a private key'

    keypair_chat = open_key_from_bytes(base64.b64decode(j['keypair_chat'].encode('utf-8')))
    assert keypair_chat.has_private, 'Chat keypair must contain a private key'

    return j['username'], keypair_login, keypair_chat


def export_account_file(username: str, keypair_login: RSA.RsaKey, keypair_chat: RSA.RsaKey) -> str:
    assert keypair_login.has_private, 'Login keypair must contain a private key'
    assert keypair_chat.has_private, 'Chat keypair must contain a private key'

    return json.dumps({
        'username': username,
        'keypair_login': base64.b64encode(keypair_login.exportKey()).decode('utf-8'),
        'keypair_chat': base64.b64encode(keypair_chat.exportKey()).decode('utf-8')
    })