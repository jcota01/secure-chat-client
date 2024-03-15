"""
This file is just to demo how the utils package works.
The specifics shown are for example and don't need to be followed exactly in the app, but it is a good place to start.

Don't use this file as part of the project.
"""
import base64
import json

from utils import crypto

if __name__ == '__main__':
    # generate two keypairs for testing
    # each keypair contains a public key and a private key
    alice_keypair = crypto.generate_rsa_keypair()
    bob_keypair = crypto.generate_rsa_keypair()

    # we make copies without the private keys just to demonstrate
    alice_publickey = alice_keypair.public_key()
    bob_publickey = bob_keypair.public_key()

    # example of a message sent from alice to bob
    # Alice -> Bob
    message = 'Hello Bob, I am Alice!'.encode('utf-8')
    print("Sending message:", message)

    # sign the message with alice's keypair, so we prove she wrote it
    signature = crypto.create_signature(message, alice_keypair)
    print("Signature:", signature)

    # encode the message and signature into a single payload (using JSON) so we can encrypt
    # we base64 encode the message and the signature in case it contains bytes we can't represent in a string easily
    # for example this could be if the message was a file
    payload = json.dumps({
        'message': base64.b64encode(message).decode('utf-8'),
        'signature': base64.b64encode(signature).decode('utf-8')
    }).encode('utf-8')
    print("Payload:", payload)

    # encrypt the payload with Bob's public key, so only he can decrypt it
    encrypted_payload = crypto.encrypt_plaintext(payload, bob_publickey)
    print("Encrypted Payload:", encrypted_payload)

    # pretend here the encrypted payload is transmitted from alice to bob
    # transmitting....
    print()
    print("Transmitting from alice to bob....")  # just pretend ok?
    print()
    # done!
    # now this runs on Bob's machine from here onwards

    print("Bob received encrypted payload:", encrypted_payload)
    # decrypt the payload using Bob's private key
    decrypted_payload = crypto.decrypt_ciphertext(encrypted_payload, bob_keypair)
    print("Decrypted payload:", decrypted_payload)

    # extract the message and the signature from the payload
    payload = json.loads(decrypted_payload.decode('utf-8'))
    # we are base64 decoding them to get the bytes back out of the payload
    message = base64.b64decode(payload['message'].encode('utf-8'))
    signature = base64.b64decode(payload['signature'].encode('utf-8'))
    print("Extracted message:", message)
    print("Extracted signature:", signature)

    # check the signature matches alice's public key, so we know she wrote it
    print("Verifying signature:")
    if crypto.verify_signature(message, signature, alice_publickey):
        print("Signature matches! The message was sent by Alice.")
        print("Received message:", message)
    else:
        print("The signature does not match! We cannot guarantee message integrity")
