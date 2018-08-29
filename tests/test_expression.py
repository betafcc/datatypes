from datatypes.expression import Add


def test_add():
    x = Add(2, 3)
    assert repr(x) == "(2 + 3)"

    x = Add(2, 3, 4)
    assert repr(x) == "(2 + 3 + 4)"
