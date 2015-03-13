"""This module defines utility functions to generate strings."""


import string
import random
import hashlib
import uuid


def random_string(size=6, chars=string.ascii_letters + string.digits):
    """Generate a random string with length equal to size.
    chars specifies the candidate characters.
    ASCII letters and digits are chosen as default."""
    return ''.join(random.choice(chars) for _ in range(size))


def sha1_hexdigest(input_string, size=20):
    """Generate hexdigest for the input string. size specifies the number
    of hex digits in the digest, which is 20 by default."""
    sha1 = hashlib.sha1()
    sha1.update(input_string)
    return sha1.hexdigest()[0:size]


def unique_id(size=40):
    """Generate unique ID. size specifies the number of characters in the
    ID, which is 40 by default."""
    return sha1_hexdigest(str(uuid.uuid1()), size).upper()
