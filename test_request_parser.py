from request_parser import RequestParser

good_req = (f"GET / HTTP/1.1\r\n"
            f"Host: www.google.com\r\n"
            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0)"
            f"Gecko/20100101 Firefox/69.0\r\n"
            f"Accept: text/html,application/xhtml+xml"
            f"application/xml;q=0.9,*/*;q=0.8\r\n"
            f"Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3\r\n"
            f"Accept-Encoding: gzip, deflate, br\r\n"
            f"Referer: https://www.google.com/\r\n"
            f"DNT: 1\r\n"
            f"Connection: keep-alive\r\n\r\n")

incomplete_req = good_req[:-50]


def test_response_parse():
    request_parser = RequestParser()
    data = good_req

    raw_data = bytearray(data, 'utf-8')
    _, parsed_req = request_parser.parse(raw_data)

    assert parsed_req.headers["Host"] == 'www.google.com'


def test_try_get_headers_ok():
    request_parser = RequestParser()
    data = good_req

    raw_data = bytearray(data, 'utf-8')
    parsed_req = request_parser.try_get_headers(raw_data)

    assert parsed_req.headers["Host"] == 'www.google.com'


def test_try_get_headers_failure():
    request_parser = RequestParser()
    data = incomplete_req

    raw_data = bytearray(data, 'utf-8')
    parsed_req = request_parser.try_get_headers(raw_data)

    assert parsed_req is None
