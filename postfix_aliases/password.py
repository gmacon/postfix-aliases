from base64 import b64encode, b64decode
import binascii
from hashlib import sha512
from hmac import compare_digest
from os import urandom


def hash_ssha512(pw):
    pw = pw.encode('utf-8')
    salt = urandom(8)
    h = sha512(pw + salt).digest()
    return (b'{SSHA512}' + b64encode(h + salt)).decode('ascii')


def check_ssha512(pw, pw_hash):
    pw = pw.encode('utf-8')
    pw_hash = pw_hash.encode('ascii')

    if not pw_hash.startswith(b'{SSHA512}'):
        return False

    try:
        hash_plus_salt = b64decode(pw_hash[9:], validate=True)
    except binascii.Error:
        return False

    hash_size = sha512().digest_size
    h = hash_plus_salt[:hash_size]
    salt = hash_plus_salt[hash_size:]

    new_h = sha512(pw + salt).digest()

    return compare_digest(h, new_h)
