from urllib.parse import urlparse, splitport


def parse_url(raw_url):
    """
    examples:
        'localhost'
        'localhost:1000'
        'rlpython://localhost:1000'
        'file://socket'

    returns (scheme, host, port)
    """

    try:
        if raw_url.startswith('file://'):
            return 'file', raw_url[7:], None

        if '://' not in raw_url:
            raw_url = 'rlpython://{}'.format(raw_url)

        parse_result = urlparse(raw_url)

        scheme = parse_result.scheme
        host, port = splitport(parse_result.netloc)
        port = int(port or '0')

        return scheme, host, port

    except Exception:
        raise ValueError(
            'invalid url format. valid formats: [HOST:]PORT, file://PATH',
        )
