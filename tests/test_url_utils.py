from url_utils import clean_url


def test_plain_url_passes_through():
    assert clean_url("https://example.com/jobs/123") == \
        "https://example.com/jobs/123"


def test_strips_whitespace():
    assert clean_url("  https://example.com  ") == "https://example.com"


def test_extracts_href_from_anchor_tag():
    raw = '<a href="https://example.com/jobs/123">Apply</a>'
    assert clean_url(raw) == "https://example.com/jobs/123"


def test_extracts_href_single_quotes():
    raw = "<a href='https://example.com/jobs/456'>Apply</a>"
    assert clean_url(raw) == "https://example.com/jobs/456"


def test_handles_empty_and_none():
    assert clean_url("") == ""
    assert clean_url(None) == ""
