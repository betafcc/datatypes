# flake8: noqa
from datatypes import compare, placeholders, substitute, run, placeholder as _


# TODO: test invalid constructors
def test_constructors():
    # keyword only
    _.x

    # positional only
    _[0]

    # keyword or positional
    _[0, "x"]

    # keyword or positional with annotation
    _[1, "x":int]

    # keyword or positional with default
    _[1, "x"::42]

    # keyword or positional with annotation and default
    _[1, "x":int:42]


def test_uniqueness():
    assert _.x is _.x
    assert _[0] is _[0]
    assert _[10, "x":int:41] is _[10, "x":int:41]


# TODO:
# - keyword only with annotation | default (maybe _["x":int:42])
# - positional only with name | annotation | default (maybe _[0,:int:42])
def test_repr():
    for var, expected in [
        # keyword only
        (_.x, "`x"),
        # positional only
        (_[0], "`0"),
        # keyword or positional
        (_[0, "x"], "`0.x"),
        # keyword or positional with annotation
        (_[0, "x":int], "`0.x:" + repr(int)),
        # keyword or positional with default
        (_[0, "x"::42], "`0.x=42"),
        # keyword or positional with annotation and default
        (_[0, "x":int:42], "`0.x:" + repr(int) + "=42"),
    ]:
        assert repr(var) == expected


def test_compare():
    did_match, results = compare(_.x, 42)
    assert did_match
    assert results == [(_.x, 42)]

    did_match, results = compare(42, _.x)
    assert did_match
    assert results == [(42, _.x)]

    assert compare(
        [1,   2, 3, _.y, {"a": _.z, "b": 6}, 7],
        [1, _.x, 3,   4, {"a":   5, "b": 6}, 7]
    ) == (True, [(2, _.x), (_.y, 4), (_.z, 5)])

    did_match, result = compare([_.x, 2], [1, 2, 3])
    assert not did_match


def test_expressions():
    _.x + 2
    _.x * _.y
    _.x(2).foo[0] + 3

    assert set(placeholders(_.x + _.y - _.y + _[0])) == {_[0], _.x, _.y}
    assert set(placeholders(_.f(arg=_.x))) == {_.f, _.x}


def test_substitute():
    assert repr(substitute(_.x + _.y)[_.y : 10]) == repr(_.x + 10)


def test_run():
    assert run(2) == 2
    assert run(substitute(_.x + 10)[_.x : 32]) == 42
