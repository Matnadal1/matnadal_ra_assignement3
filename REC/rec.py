from collections import OrderedDict
from typing import Callable, List, Dict

class Element:
    def __init__(self, value):
        self.value = value
        self.count = 1

    def increment(self):
        self.count += 1

    def __repr__(self):
        return f"Element(value='{self.value}', count={self.count})"

class Recordinality:
    def __init__(
        self, k: int, 
        hashfunc: Callable[[str], float]
        ):
        self.k = k
        self.hashfunc = hashfunc
        self.k_map = OrderedDict()
        self.modifications = 0
        self.cached_min = float('-inf')
    
    def run_rec(self, stream_list):
        for element in stream_list:
            self.update(element)

    def update(self, element: str):
        inserted = self._insert_if_fits(element)
        if inserted:
            self.modifications += 1

    def estimate_cardinality(self):
        pow_factor = self.modifications - self.k + 1
        estimate = (self.k * ((1 + (1.0 / self.k)) ** pow_factor)) - 1
        return int(estimate)

    def _insert_if_fits(self, element: str):
        hashed_value = self.hashfunc(element)

        if hashed_value < self.cached_min and len(self.k_map) >= self.k:
            return False

        if hashed_value in self.k_map:
            self.k_map[hashed_value].increment()
            return False
        else:
            if len(self.k_map) < self.k:
                self.k_map[hashed_value] = Element(element)
                self.cached_min = min(self.k_map.keys())
            else:
                lowest_key = min(self.k_map.keys())
                if hashed_value > lowest_key:
                    del self.k_map[lowest_key]
                    self.k_map[hashed_value] = Element(element)
                    self.cached_min = min(self.k_map.keys())
                else:
                    return False
            return True

    def __repr__(self):
        return (f"Recordinality(k={self.k}, modifications={self.modifications}, "
                f"cached_min={self.cached_min}, est_cardinality={self.estimate_cardinality()})")
