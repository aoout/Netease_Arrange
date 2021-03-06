'''
The password required to log in to NetEase Cloud Music,
and the parameters required for subsequent requests need to be encrypted.
This module presents these encryption algorithms.
'''

# pylint:disable = missing-function-docstring,invalid-name
import base64
import binascii
import json
import os
from hashlib import md5

from Cryptodome.Cipher import AES

MODULUS = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
    "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
    "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
    "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
    "3ece0462db0a22b8e7"
)
PUBKEY = "010001"

NONCE = b"0CoJUm6Qyw8W8jud"


def encrypted_request(text):
    data = json.dumps(text).encode("utf-8")
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encSecKey = rsa(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encSecKey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16),
             int(pubkey, 16), int(modulus, 16))
    return format(rs, "x").zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]


def encrypted_password(password):
    return md5(password.encode('utf-8')).hexdigest()
