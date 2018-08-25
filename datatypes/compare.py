import collections.abc
from functools import singledispatch, reduce
from typing import Any, Tuple, List


def compare(a: Any, b: Any) -> Tuple[bool, List[Tuple]]:
    ta, tb = type(a), type(b)

    if hasattr(ta, "_compare_"):
        return ta._compare_(a, b)
    if hasattr(tb, "_rcompare_"):
        return tb._rcompare_(b, a)

    if ta != tb:
        return (False, [])

    return homo_compare(a, b)


def concat(
    left: Tuple[bool, List[Tuple]], right: Tuple[bool, List[Tuple]]
) -> Tuple[bool, List[Tuple]]:
    l_ismatch, l_map = left
    r_ismatch, r_map = right
    return (l_ismatch and r_ismatch, l_map + r_map)


compare.concat = concat


@singledispatch
def homo_compare(a, b) -> Tuple[bool, List[Tuple]]:
    return (a == b, [])


@homo_compare.register
def _(a: collections.abc.Sequence, b: collections.abc.Sequence):
    return reduce(concat, map(compare, a, b), (len(a) == len(b), []))
