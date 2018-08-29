import pytest

from datatypes import match
from datatypes.protocols.match import NoMatchError


def test_match_base():
    x = 1
    assert (
        match(x)[
            0:"zero",
            1:"one",
            2:"two",
            3:"three",
            4:"Lorem ipsum dolor sit amet, consectetur",
        ]
        == "one"
    )

    x = "hello"
    assert match(x)["hello world":False, "bonjour":False, "hello":True, "oi":False]

    x = "foo"
    assert match(x)["bar":False, "biz":False, ...:True]

    with pytest.raises(NoMatchError):
        match("foo")["bar":"biz"]


def test_match_single():
    assert match(10)[10:True]
    assert not match(10)[10:False]


def test_match_list():
    assert match([1, 2, 3])[[1, 2, 3]:True]
    assert not match([1, 2, 3])[[1, 2, 3]:False]
    assert match([1, 2, 3])[[1, 2, 3]:True, [3, 2, 1]:False]

    assert match([1, 2, 3])[[1, 2, 5]:False, [3, 2, 1]:False, ...:True]

    with pytest.raises(NoMatchError):
        match([1, 2, 3])[[1, 2, 5]:False, [3, 2, 1]:False]


def test_match_dict():
    assert match({"a": 1, "b": 2})[
        {"a": 1, "b": 2, "c": 3}:False, {"a": 1, "b": 2}:True, {"a": 1, "b": 2}:False
    ]
