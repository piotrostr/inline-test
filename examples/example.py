from intest import test, before_all, before_each, after_each


@before_all
def setup_all():
    print("Running before all tests")


@test()
def test_something():
    assert 1 + 1 == 2


@test(skip=True, skip_reason="Not implemented yet")
def test_skipped():
    pass


def add(a: int, b: int) -> int:
    return a + b


state = {"count": 0}


@before_each
def setup():
    state["count"] = 0


@after_each
def teardown():
    state["count"] = 0


@test(tag="math")
def test_add():
    assert add(2, 2) == 4
    state["count"] += 1


@test(tag="math")
def test_add_negative():
    assert add(-2, -2) == -4
    state["count"] += 1


@test()
def test_that_fails():
    assert 1 == 2, "This test should fail"


@test()
def test_that_checks_if_state_is_reset():
    assert state["count"] == 0
