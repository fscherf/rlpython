from urllib.parse import urlparse, splitport


def parse_url(raw_url):
    try:
        if isinstance(raw_url, int):
            raw_url = str(raw_url)

        if raw_url.startswith('file://'):
            return 'file', raw_url[7:], None

        parse_result = urlparse(raw_url)

        if not parse_result.scheme:
            raw_url = 'rlpython://{}'.format(raw_url)
            parse_result = urlparse(raw_url)

        scheme = parse_result.scheme
        host = parse_result.netloc
        port = parse_result.port

        if port is None:
            port = host
            host = 'localhost'

        host = splitport(host)[0]

        return scheme, host, int(port)

    except Exception:
        raise ValueError(
            'invalid url format. valid formats: [HOST:]PORT, file://PATH',
        )
