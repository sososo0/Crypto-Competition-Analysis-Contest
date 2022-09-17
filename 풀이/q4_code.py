import base64
import base58
import binascii
import hashlib
import hmac
import unicodedata
import ecdsa
import itertools


class InvalidKeyError(Exception):
    def __init__(self, message):
        super().__init__(message)


SECP256k1 = ecdsa.curves.SECP256k1
CURVE_GEN = ecdsa.ecdsa.generator_secp256k1
CURVE_ORDER = CURVE_GEN.order()
FIELD_ORDER = SECP256k1.curve.p()
INFINITY = ecdsa.ellipticcurve.INFINITY


def big_endian_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


def hmac_sha512(key: bytes, msg: bytes):
    return hmac.new(key=key, msg=msg, digestmod=hashlib.sha512).digest()


def master_key(bip39_seed, testnet=False):
    I = hmac_sha512(key=b"Bitcoin seed", msg=bip39_seed)
    i_left = I[:32]  # 256나누기 8은??
    int_left_key = big_endian_to_int(i_left)
    if int_left_key == 0:
        raise InvalidKeyError("master key is zero")
    if int_left_key >= CURVE_ORDER:
        raise InvalidKeyError("master key {} is greater/equal to curve order".format(int_left_key))
    # chain code
    i_right = I[32:]

    return i_left, i_right  # KEY, chaincode


def get_xpriv_from_master(priv_key, chaincode):
    xprv = b'\x04\x88\xad\xe4'  # bitcoin private main net
    xprv += b'\x00' * 9  # Depth, fingerprint, child
    xprv += chaincode  # chain code
    xprv += b'\x00' + priv_key  # Master key

    hashed_xprv = hashlib.sha256(xprv).digest()
    hashed_xprv = hashlib.sha256(hashed_xprv).digest()

    xprv += hashed_xprv[:4]
    return base58.b58encode(xprv)


def get_xpub_from_master(priv_key, chaincode):
    point = CURVE_GEN * int.from_bytes(priv_key, byteorder='big')

    if point.y() & 1:
        pub = b'\x03'
    else:
        pub = b'\x02'
    pub += ecdsa.util.number_to_string(point.x(), CURVE_ORDER).rjust(32, b'\x00')  # compressed key
    # xpub += ecdsa.util.number_to_string(point.y(), CURVE_ORDER).rjust(32, b'\x00')

    xpub = b'\x04\x88\xb2\x1e'
    xpub += b'\x00' * 9
    xpub += chaincode
    xpub += pub

    checksum = hashlib.sha256(hashlib.sha256(xpub).digest()).digest()[:4]
    return base58.b58encode(xpub + checksum)


def permutation(word_list, r):
    wordlist_values = []
    for v in word_list:
        wordlist_values.append(v)

    result = itertools.permutations(wordlist_values, r)
    return result


def find_priv_key(word_list, r=12, passphrase=''):
    global xPubKey
    salt = 'mnemonic' + passphrase
    every_mnemonic_sentence = permutation(word_list, r)

    i = 0

    for sentence in every_mnemonic_sentence:
        mnemonic_code = ' '.join(sentence)
        seed = hashlib.pbkdf2_hmac("sha512", mnemonic_code.encode('utf-8'), salt.encode('utf-8'), 2048)
        master_priv_key, chain_code = master_key(seed)
        master_pub_key = get_xpub_from_master(master_priv_key, chain_code)
        if master_pub_key == xPubKey:
            print(f"private key found: {master_priv_key}")
            break
        print(f"{i} checked")
        i += 1


if __name__ == "__main__":
    word_dict = {"abandon": 0, "bright": 224, "business": 248, "color": 365, "jelly": 958, \
                 "joy": 964, "license": 1033, "mercy": 1114, "mountain": 1156, "this": 1798, \
                 "payment": 1293, "prefer": 1358, "quality": 1401, "power": 1354, "zoo": 2047}
    wordlist = ["abandon", "bright", "business", "color", "jelly", "joy", "license", "mercy", "mountain", "this", \
                "payment", "prefer", "quality", "power", "zoo"]
    mnemonic_ct = 'NjuugzjFTbX7Tj05w4FVpPnyP9lru7uFtPRPwkn1nQGprvFirzHSjLVCipWEJqUayFb/Ksm46yIWtbPCTF0viJUD4+lcBcSlpMpBuwxBc92yUaQ5aE8lX21s'
    xpriv_ct = 'kN197TSnBiyqHv+Ul1ioNdvmNZV3zDSkane+qTrLKLoJaeTh2mUooYKYY+EgztWp6ichJfqUWCM0D9Yd72j4Ytj4wVLVRP+5VcUBqpnHli2gVIYIETocig92bNCzIZdb42jheXbRd+EvH5ZSanq3Sr3uQJN/eN0='

    print(len(base64.b64decode(mnemonic_ct)))
    print(len(base64.b64decode(xpriv_ct)))

    mnemonic = ''
    mnemonic = mnemonic.encode()
    xPubKey = b'xpub661MyMwAqRbcFwkbijMsskkrPEja9rZQAvGavNLGpthpwzbPyBDjCFUiLHVQXED2YM9pUAC7zz62ShWRPRdwbyyWEQ5CK1yP5vPWrmGCg7D'
    # salt = base64.b64decode('2B2CnAzrhrU=')
    # print(salt)

    # TEST
    # https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#test-vector-1
    pr, chain = master_key(b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')
    print(get_xpriv_from_master(pr, chain))
    print(get_xpub_from_master(pr, chain))

    # https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#test-vector-2
    pr, chain = master_key(
        b'\xff\xfc\xf9\xf6\xf3\xf0\xed\xea\xe7\xe4\xe1\xde\xdb\xd8\xd5\xd2\xcf\xcc\xc9\xc6\xc3\xc0\xbd\xba\xb7\xb4\xb1\xae\xab\xa8\xa5\xa2\x9f\x9c\x99\x96\x93\x90\x8d\x8a\x87\x84\x81\x7e\x7b\x78\x75\x72\x6f\x6c\x69\x66\x63\x60\x5d\x5a\x57\x54\x51\x4e\x4b\x48\x45\x42')
    print(get_xpriv_from_master(pr, chain))
    print(get_xpub_from_master(pr, chain))

    find_priv_key(wordlist)
