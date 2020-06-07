from request import Request


class RequestParser:
    def get_destination(self, request: Request):

        host_name = request.path.split("//")[-1].split("/")[0].strip()

        if 'Host' in request.headers.keys():
            host_name = request.headers['Host']

        connect_port = 80
        if ":" in host_name:
            host_name = host_name.split(':')
            connect_port = int(host_name[1])
            host_name = host_name[0]

        return host_name, connect_port

    def parse(self, data):
        """Parse raw request and return Request object
        :type data: bytearray
        """
        try:
            headers_end = self.get_headers_end(data)
        except ValueError:
            return None, None
        body_raw = data[headers_end:]
        head_fields = data[:headers_end]\
            .decode('utf-8', errors='ignore')\
            .splitlines()
        headers = {}
        for field in head_fields[1:-1]:
            try:
                key, value = field.split(':', maxsplit=1)
                headers[key] = value.strip()
            except ValueError:
                continue
        return headers, Request(head_fields[0], headers, body_raw, data[:headers_end])

    @staticmethod
    def get_headers_end(request_raw):
        """Get index of header block ending in the provided client request
        :type request_raw: bytearray
        """
        end_line = bytearray(b'\r\n\r\n')
        try:
            headers_end = request_raw.index(end_line) + len(end_line)
        except ValueError:
            raise ValueError('Failed to process headers. Aborting.')
        return headers_end
