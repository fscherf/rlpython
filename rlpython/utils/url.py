def parse_url(url):
    if isinstance(url, int):
        return 'localhost', url

    try:
        if ':' in url:
            host, port = url.split(':')
            port = int(port)

            return host, port

        else:
            port = int(url)

            return 'localhost', port

    except Exception:
        raise ValueError('invalid url format')
