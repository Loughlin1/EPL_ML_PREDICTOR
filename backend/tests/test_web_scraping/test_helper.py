import pytest

from app.services.web_scraping.fixtures.helper import match_on_name


def test_basic():
    assert match_on_name("J. Doe") == "J. Doe"

def test_special_characters():
    assert match_on_name("G. Rodríguez") == "G. Rodríguez"
    assert match_on_name("N. Füllkrug") == "N. Füllkrug"

def test_match_full_first_name():
    assert match_on_name("Luis Guilherme") == "Luis Guilherme"

def test_match_captain():
    assert match_on_name("J. Bowen (c)") == "J. Bowen"

def test_no_match_on_substitution():
    assert match_on_name("M. Kudus 73'") is None

def test_match_double_barrell_lastname():
    assert match_on_name("J. Ward-Prowse") == "J. Ward-Prowse"


if __name__ == "__main__":
    pytest.main()