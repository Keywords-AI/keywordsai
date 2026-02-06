import hashlib
import secrets
from types import NoneType
import datetime
from decimal import Decimal
import typing
RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
UNUSABLE_PASSWORD_PREFIX = "!"  # This will never be a valid encoded hash
UNUSABLE_PASSWORD_SUFFIX_LENGTH = (
    40  # number of random chars to add after UNUSABLE_PASSWORD_PREFIX
)
_PROTECTED_TYPES = (
    NoneType,
    int,
    float,
    Decimal,
    datetime.datetime,
    datetime.date,
    datetime.time,
)


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_str(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)
def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return "".join(secrets.choice(allowed_chars) for i in range(length))

def force_bytes(s, encoding="utf-8", strings_only=False, errors="strict"):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == "utf-8":
            return s
        else:
            return s.decode("utf-8", errors).encode(encoding, errors)
    if strings_only and is_protected_type(s):
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    return str(s).encode(encoding, errors)


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return secrets.compare_digest(force_bytes(val1), force_bytes(val2))

def concatenate(left: str, right: str) -> str:
    return "{}.{}".format(left, right)


def split(concatenated: str) -> typing.Tuple[str, str]:
    left, _, right = concatenated.partition(".")
    return left, right


class Sha512ApiKeyHasher:
    """
    An API key hasher using the sha512 algorithm.

    This hasher should *NEVER* be used in Django's `PASSWORD_HASHERS` setting.
    It is insecure for use in hashing passwords, but is safe for hashing
    high entropy, randomly generated API keys.
    """

    algorithm = "sha512"

    def salt(self) -> str:
        """No need for a salt on a high entropy key."""
        return ""

    def encode(self, password: str, salt: str) -> str:
        if salt != "":
            raise ValueError("salt is unnecessary for high entropy API tokens.")
        hash = hashlib.sha512(password.encode()).hexdigest()
        return "%s$$%s" % (self.algorithm, hash)

    def verify(self, password: str, encoded: str) -> bool:
        encoded_2 = self.encode(password, "")
        return constant_time_compare(encoded, encoded_2)


class KeyGenerator:
    preferred_hasher = Sha512ApiKeyHasher()

    def __init__(self, prefix_length: int = 8, secret_key_length: int = 32):
        self.prefix_length = prefix_length
        self.secret_key_length = secret_key_length

    def get_prefix(self) -> str:
        return get_random_string(self.prefix_length)

    def get_secret_key(self) -> str:
        return get_random_string(self.secret_key_length)

    def hash(self, value: str) -> str:
        if value is None:
            return UNUSABLE_PASSWORD_PREFIX + get_random_string(
                UNUSABLE_PASSWORD_SUFFIX_LENGTH
            )
        if not isinstance(value, (bytes, str)):
            raise TypeError(
                "Password must be a string or bytes, got %s." % type(value).__qualname__
            )
        hasher = self.preferred_hasher
        return hasher.encode(value, "")

    def generate(self) -> typing.Tuple[str, str, str]:
        prefix = self.get_prefix()
        secret_key = self.get_secret_key()
        key = concatenate(prefix, secret_key)
        hashed_key = self.hash(key)
        return key, prefix, hashed_key

    def verify(self, key: str, hashed_key: str) -> bool:
        result = self.preferred_hasher.verify(key, hashed_key)
        return result

    def using_preferred_hasher(self, hashed_key: str) -> bool:
        return hashed_key.startswith(f"{self.preferred_hasher.algorithm}$$")
        
