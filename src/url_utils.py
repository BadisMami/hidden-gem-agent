import re

_ANCHOR_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def clean_url(raw_url):
    """
    Normalize a URL value into a plain string.

    Handles values that were accidentally stored as HTML anchor tags
    (e.g. copy-pasted from a browser or chat), such as:
        <a href="https://example.com">Apply</a>
    and returns just the plain URL string. Already-plain URLs pass through
    unchanged (aside from stripping whitespace).
    """

    if raw_url is None:
        return ""

    raw_url = str(raw_url).strip()

    if not raw_url:
        return ""

    match = _ANCHOR_HREF_RE.search(raw_url)

    if match:
        return match.group(1).strip()

    return raw_url
