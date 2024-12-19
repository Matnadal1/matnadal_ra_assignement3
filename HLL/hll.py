from __future__ import annotations
from randomhash import RandomHashFamily
import numpy as np
import warnings
import struct
from typing import Callable, Optional

# Get the number of bits starting from the first non-zero bit to the right
_bit_length = lambda bits: bits.bit_length()
if not hasattr(int, "bit_length"):
    _bit_length = lambda bits: len(bin(bits)) - 2 if bits > 0 else 0

class HyperLogLog(object):
    """
    Args:
        p (int): The precision parameter. It is ignored if
            the `reg` is given.
        hashfunc (Callable): The hash function used by this MinHash.
            It takes the input passed to the `update` method and
            returns an integer that can be encoded with 32 bits.
            The default hash function is based on SHA1 from hashlib_.
    """

    __slots__ = ("p", "m", "reg", "alpha", "max_rank", "hashfunc")

    # The range of the hash values used for HyperLogLog
    _hash_range_bit = 32
    _hash_range_byte = 4

    def _get_alpha(self, p):
        if not (4 <= p <= 16):
            raise ValueError("p=%d should be in range [4 : 16]" % p)
        if p == 4:
            return 0.673
        if p == 5:
            return 0.697
        if p == 6:
            return 0.709
        return 0.7213 / (1.0 + 1.079 / (1 << p))

    def __init__(
        self,
        p: int = 8,
        hashfunc: Callable = None,
    ):
        self.p = p
        self.m = 1 << p
        self.reg = np.zeros((self.m,), dtype=np.int8)

        # Check the hash function.
        if hashfunc is None:
            random_hash_family = RandomHashFamily(count=1)  # Une seule fonction de hachage
            self.hashfunc = lambda x: random_hash_family.hashes(str(x))[0]
        elif not callable(hashfunc):
            raise ValueError("The hashfunc must be a callable.")
        else:
            self.hashfunc = hashfunc
        # Common settings
        self.alpha = self._get_alpha(self.p)
        self.max_rank = self._hash_range_bit - self.p

    def add_elements_to_hll(self, stream_list):
        for d in stream_list:
            self.update(str(d).encode('utf8'))
            
    def update(self, b):
        """
        Update the HyperLogLog with a new data value in bytes.
        The value will be hashed using the hash function specified by
        the `hashfunc` argument in the constructor.

        Args:
            b: The value to be hashed. Can be bytes, str, or int.
        """
        # Handle integers by converting them to strings
        if isinstance(b, int) or isinstance(b, np.integer):
            b = str(b).encode('utf8')
        elif isinstance(b, str):
            b = b.encode('utf8')

        # Digest the hash object to get the hash value
        hv = int(self.hashfunc(b))  
        # Get the index of the register using the first p bits of the hash
        reg_index = hv & (self.m - 1)
        # Get the rest of the hash
        bits = hv >> self.p
        # Update the register
        self.reg[reg_index] = max(self.reg[reg_index], self._get_rank(bits))

    def count(self):
        """
        Estimate the cardinality of the data values seen so far.

        Returns:
            float: The estimated cardinality.
        """
        # Use HyperLogLog estimation function
        e = self.alpha * float(self.m**2) / np.sum(2.0 ** (-self.reg))
        # Small range correction
        small_range_threshold = (5.0 / 2.0) * self.m
        if abs(e - small_range_threshold) / small_range_threshold < 0.15:
            warnings.warn(
                (
                    "Warning: estimate is close to error correction threshold. "
                    + "Output may not satisfy HyperLogLog accuracy guarantee."
                )
            )
        if e <= small_range_threshold:
            num_zero = self.m - np.count_nonzero(self.reg)
            return self._linearcounting(num_zero)
        # Normal range, no correction
        if e <= (1.0 / 30.0) * (1 << 32):
            return e
        # Large range correction
        return self._largerange_correction(e)

    def _get_rank(self, bits):
        rank = self.max_rank - _bit_length(bits) + 1
        if rank <= 0:
            raise ValueError(
                "Hash value overflow, maximum size is %d\
                    bits"
                % self.max_rank
            )
        return rank

    def _linearcounting(self, num_zero):
        return self.m * np.log(self.m / float(num_zero))

    def _largerange_correction(self, e):
        return -(1 << 32) * np.log(1.0 - e / (1 << 32))