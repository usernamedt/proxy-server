class ResponseParser:
    def parse(self, data):
        """Parse response, return status, headers and cookies if exist"""
        headers_end = self.get_headers_end(data)
        body_raw = data[headers_end:]
        head_fields = data[:headers_end]\
            .decode('utf-8', errors='ignore')\
            .splitlines()

        processed_fields = [head_fields[0]]
        headers = {}
        for field in head_fields[1:-1]:
            try:
                key, value = field.split(':', maxsplit=1)
                headers[key] = value.strip()
            except ValueError:
                continue
            # cut set-cookie header
            if "set-cookie" in field.lower():
                continue
            processed_fields.append(field)
        processed_fields.append(head_fields[-1])
        modified_headers = ('\r\n'.join(processed_fields) + '\r\n').encode('utf-8', errors='ignore')
        return headers, modified_headers, body_raw

    @staticmethod
    def get_headers_end(response_raw):
        """Get index of header block ending in the provided server response"""
        end_line = bytearray(b'\r\n\r\n')
        try:
            headers_end = response_raw.index(end_line) + len(end_line)
        except Exception:
            raise Exception('Failed to process headers. Aborting.')
        return headers_end
