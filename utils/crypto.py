from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from utils import RSA_KEY_BITS


def generate_rsa_keypair() -> RSA.RsaKey:
    """
    Securely generates a new RSA key pair of bit-size utils.RSA_KEY_BITS
    :return: A new RSA keypair
    """
    return RSA.generate(RSA_KEY_BITS)


def open_key_from_bytes(key: bytes) -> RSA.RsaKey:
    """
    Produces an RSA key object from bytes
    :param key: The bytes of an RSA key from key.export_key()
    :return: An RSA key object
    """
    return RSA.import_key(key)


def open_key_from_file(file_path: str) -> RSA.RsaKey:
    """
    Produces an RSA key object from a file path (this is a thin wrapper around utils.crypto.open_key_from_bytes)
    :param file_path: The path to a file containing bytes of an RSA key produced by key.export_key()
    :return: An RSA key object
    """
    f = open(file_path, 'rb')
    key: RSA.RsaKey = open_key_from_bytes(f.read())
    f.close()
    return key


def create_signature(message: bytes, private_key: RSA.RsaKey) -> bytes:
    """
    Create a signature for a given message using a private key
    :param message: The plaintext message you wish to create a signature for
    :param private_key: The private key you want to use to sign the message with
    :return: The signature bytes (note: the signature does not contain the plaintext message itself)
    """
    assert private_key.has_private(), "Provided key must have a private key component to sign"
    h = SHA256.new(message)
    return pss.new(private_key).sign(h)


def verify_signature(message: bytes, signature: bytes, public_key: RSA.RsaKey) -> bool:
    """
    Verify the signature of a message is valid, given the public key of the party who allegedly signed it
    :param message: The plaintext message which the signature was allegedly created for
    :param signature: The signature which was allegedly generated for the message
    :param public_key:  The public key of the party who signed the message
    :return: Returns True if the signature is valid, otherwise False
    """
    h = SHA256.new(message)
    verifier = pss.new(public_key)
    try:
        verifier.verify(h, signature)
        return True
    except ValueError:
        return False


def encrypt_plaintext(plaintext: bytes, public_key: RSA.RsaKey) -> bytes:
    """
    Encrypts a plaintext message using a public key so only the party with the corresponding private key can decrypt it
    :param plaintext: The message you want to encrypt
    :param public_key: The public key you want to encrypt with
    :return: The ciphertext of the message
    """
    cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)

    # this asymmetric crypto only supports encrypting blocks up to a certain block size, so we work out what that is
    # and split the message up into blocks of that size

    # algorithm taken from pycryptodome docs
    #                        (public key size in bytes     ) - 2 - (2 * hash algorithm size in bytes)
    max_encrypt_block_size = (public_key.size_in_bits() // 8) - 2 - (2 * (256//8)                     )
    overall_ciphertext = bytearray()

    # encrypt each block
    for block in range((len(plaintext) + max_encrypt_block_size - 1) // max_encrypt_block_size):
        overall_ciphertext += cipher.encrypt(plaintext[block * max_encrypt_block_size:(block+1) * max_encrypt_block_size])

    return bytes(overall_ciphertext)


def decrypt_ciphertext(ciphertext: bytes, private_key: RSA.RsaKey) -> bytes:
    """
    Decrypts a ciphertext message using a private key
    :param ciphertext: The message you want to decrypt
    :param private_key: The private key that corresponds to the public key the message was encrypted with
    :return: The plaintext of the message
    """
    assert private_key.has_private(), "Provided key must have a private key component to decrypt"
    cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    # this asymmetric crypto only supports encrypting blocks up to a certain block size, so we work out what that is
    # and split the message up into blocks of that size

    # algorithm taken from pycryptodome docs
    #                        (private key size in bytes      )
    max_decrypt_block_size = (private_key.size_in_bits() // 8)
    overall_plaintext = bytearray()

    # decrypt each block
    for block in range((len(ciphertext) + max_decrypt_block_size - 1) // max_decrypt_block_size):
        overall_plaintext += cipher.decrypt(ciphertext[block * max_decrypt_block_size:(block+1) * max_decrypt_block_size])

    return bytes(overall_plaintext)
