from response_parser import ResponseParser
from cookie_processor import CookieProcessor


def test_response_parse():
    response_parser = ResponseParser()
    cookie_processor = CookieProcessor()
    domain = "use.typekit.net"
    data = (
        f"HTTP/2.0 200 OK \r\n"
        f"access-control-allow-origin: *\r\n"
        f"cache-control: public, max-age=31536000\r\n"
        f"content-type: application/font-woff2\r\n"
        f"etag: 3c1586c61e2fb94af4085b2b3bcd2f3f43612c48\r\n"
        f"server: nginx\r\n"
        f"timing-allow-origin: *\r\n"
        f"content-length: 19648\r\n"
        f"date: Sun, 02 Jun 2019 19:25:18 GMT\r\n"
        f"X-Firefox-Spdy: h2\r\n\r\n"
    )
    raw_data = bytearray(data, 'utf-8')
    _, headers, _ = response_parser.parse(
        raw_data, domain, '\\', cookie_processor)
    assert headers["date"] == 'Sun, 02 Jun 2019 19:25:18 GMT'
