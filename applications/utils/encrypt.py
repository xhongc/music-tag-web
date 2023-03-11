from json import dumps
from os import urandom
from base64 import b64encode
from binascii import hexlify
from hashlib import md5

from Cryptodome.Cipher import AES

__all__ = ["weEncrypt", "linuxEncrypt", "eEncrypt", "MD5"]

MODULUS = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
    "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
    "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
    "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
    "3ece0462db0a22b8e7"
)
PUBKEY = "010001"
NONCE = b"0CoJUm6Qyw8W8jud"
LINUXKEY = b"rFgB&h#%2?^eDg:Q"
EAPIKEY = b'e82ckenh8dichen8'


def MD5(value):
    m = md5()
    m.update(value.encode())
    return m.hexdigest()


def weEncrypt(text):
    """
    引用自 https://github.com/darknessomi/musicbox/blob/master/NEMbox/encrypt.py#L40
    """
    data = dumps(text).encode("utf-8")
    secret = create_key(16)
    method = {"iv": True, "base64": True}
    params = aes(aes(data, NONCE, method), secret, method)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encseckey}


def linuxEncrypt(text):
    """
    参考自 https://github.com/Binaryify/NeteaseCloudMusicApi/blob/master/util/crypto.js#L28
    """
    text = str(text).encode()
    data = aes(text, LINUXKEY)
    return {"eparams": data.decode()}


def eEncrypt(url, text):
    text = str(text)
    digest = MD5("nobody{}use{}md5forencrypt".format(url, text))
    data = "{}-36cd479b6b5-{}-36cd479b6b5-{}".format(url, text, digest)
    return {"params": aes(data.encode(), EAPIKEY)}


def aes(text, key, method={}):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    if "iv" in method:
        encryptor = AES.new(key, AES.MODE_CBC, b"0102030405060708")
    else:
        encryptor = AES.new(key,  AES.MODE_ECB)
    ciphertext = encryptor.encrypt(text)
    if "base64" in method:
        return b64encode(ciphertext)
    return hexlify(ciphertext).upper()


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(hexlify(text), 16),
             int(pubkey, 16), int(modulus, 16))
    return format(rs, "x").zfill(256)


def create_key(size):
    return hexlify(urandom(size))[:16]
