# flake8: noqa
from typing import Generic, TypeVar

from datatypes import __version__, datatype


def test_version():
    assert __version__ == "0.1.0"


A = TypeVar("A")


@datatype(expose=locals())
class Maybe(Generic[A]):
    Just: A
    Nothing: ()

    def fmap(self, f):
        from datatypes import match, placeholder as _

        return match(self)[Just(_.x) : Just(f << _.x), Nothing() : Nothing()]


def test_main_example():
    assert Maybe
    assert Maybe.Just is Just
    assert Maybe.Nothing is Nothing

    assert Just(10) == Just(10)
    assert not (Just(10) == Just(11))
    assert Nothing() == Nothing()

    assert repr(Just(10)) == "Just(10)"
    assert repr(Nothing()) == "Nothing()"


def test_match():
    from datatypes import match, compare, substitute, placeholder as _

    m = Just(10)

    did_match, results = compare(m, Just(_.x))
    assert did_match
    assert results == [(10, _.x)]

    assert substitute(Just(_.x), {_.x: 10}) == Just(10)

    assert match(m)[
        Nothing() : False, Just(1) : False, Just(10) : True, Just(11) : False
    ]

    assert Just(100) == match(m)[Just(10) : Just(100)]

    assert 11 == match(Just(10))[Nothing() : Nothing(), Just(_.x) : _.x + 1]

    assert match(Nothing())[Nothing(): True]

# def test_fmap():
#     assert Just(10).fmap(lambda x: x ** 2) == Just(100)
