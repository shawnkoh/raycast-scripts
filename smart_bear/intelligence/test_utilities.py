from attrs import asdict


def assert_that(a, b):
    assert asdict(a) == asdict(b)
