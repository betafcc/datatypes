import collections.abc
from functools import singledispatch, reduce
from typing import Any, Tuple, List


CompareResult = Tuple[bool, List[Tuple]]


class compare:
    def __new__(cls, a: Any, b: Any) -> CompareResult:
        ta, tb = type(a), type(b)

        if hasattr(ta, "_compare_"):
            return ta._compare_(a, b)

        if hasattr(tb, "_rcompare_"):
            return tb._rcompare_(b, a)

        if ta != tb:
            return compare.negative([])

        return homo_compare(a, b)

    @staticmethod
    def negative(values: List[Tuple] = None) -> CompareResult:
        return (False, values or [])

    @staticmethod
    def positive(values: List[Tuple] = None) -> CompareResult:
        return (True, values or [])

    @staticmethod
    def concat(left: CompareResult, right: CompareResult) -> CompareResult:
        l_ismatch, l_map = left
        r_ismatch, r_map = right
        return (l_ismatch and r_ismatch, l_map + r_map)


@singledispatch
def homo_compare(a, b) -> CompareResult:
    return (a == b, [])


@homo_compare.register  # type: ignore
def _(a: collections.abc.Sequence, b: collections.abc.Sequence):
    return reduce(compare.concat, map(compare, a, b), (len(a) == len(b), []))


@homo_compare.register  # type: ignore
def _(a: dict, b: dict):
    keys_a, keys_b = set(a), set(b)
    keys_ab = keys_a.intersection(keys_b)

    return reduce(
        compare.concat, (compare(a[k], b[k]) for k in keys_ab), (keys_a == keys_b, [])
    )
