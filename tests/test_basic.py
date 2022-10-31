from hkfs import __version__,  main


def test_version():
    assert __version__ == "0.1.0"


def test_has_main():
    assert callable(main)
