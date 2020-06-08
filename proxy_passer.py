import logging
import socket
from select import select
import traceback

from request_parser import RequestParser
from response_parser import ResponseParser
from server_config import ServerConfig


class ProxyPasser:
    __config = ServerConfig()
    __req_parser = RequestParser()
    __res_parser = ResponseParser()

    def __init__(self, client_socket):
        self.__client = client_socket
        self.__target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        """
        Init connection client <> target
        :return:
        """
        logging.info(f"Client <> Target opened")

        raw_req = self.__client.recv(8192)
        if raw_req is None:
            logging.info(f"Client terminated (RECV)")
            self.__client.close()
            return
        _, req = self.__req_parser.parse(raw_req)
        host, port = self.__req_parser.get_destination(req)

        full_body = None
        content_len = req.headers.get('Content-Length')
        if content_len:
            full_body = self._read_http_message_content_length(self.__client, req.body, int(content_len))

        transfer_enc = req.headers.get('Transfer-Encoding')
        if transfer_enc == 'chunked':
            full_body = self._read_http_message_chunked_encoding(self.__client, req.body)

        if req.method not in ['POST','PUT', 'PATCH']:
            raw_req = req.headers_raw
        else:
            if not full_body:
                self.__client.close()
                return
            raw_req = req.headers_raw + full_body

        target_host_socket = self.__target
        target_host_socket.connect((host, port))
        target_host_socket.sendall(raw_req)

        raw_rsp = target_host_socket.recv(8192)
        if raw_rsp is None:
            logging.info(f"Server terminated (RECV)")
            self.__close_conn(target_host_socket)
            return
        orig_headers, mod_headers, body = self.__res_parser.parse(raw_rsp)

        full_body = None
        content_len = orig_headers.get('Content-Length')
        if content_len:
            full_body = self._read_http_message_content_length(target_host_socket, body, int(content_len))

        transfer_enc = orig_headers.get('Transfer-Encoding')
        if transfer_enc == 'chunked':
            full_body = self._read_http_message_chunked_encoding(target_host_socket, body)
        # if not full_body:
        #     return
        final_response = mod_headers + full_body
        self.__client.sendall(final_response)
        self.__close_conn(target_host_socket)


    def _read_http_message_content_length(self, client, body_bytes, total_len):
        """Reads request data from socket. If request method or protocol
        are not supported, rejects it"""
        result = body_bytes
        curr_len = len(body_bytes)
        while curr_len < total_len:
            chunk = client.recv(8192)
            if not chunk:
                break
            result += chunk
            curr_len += len(chunk)
        return result

    def _read_http_message_chunked_encoding(self, client, body_bytes):
        """Reads request data from socket. If request method or protocol
                are not supported, rejects it"""
        result = bytearray()
        avail_read = 0
        while True:
            if len(body_bytes) < 2:
                chunk = client.recv(8192)
                if not chunk:
                    break
                body_bytes += chunk

            if avail_read > 0:
                fragment = body_bytes[:avail_read]
                result += fragment
                body_bytes = body_bytes[avail_read:]
                avail_read -= len(fragment)
                if avail_read < 0:
                    avail_read = 0
            else:
                body_decoded = body_bytes.decode('utf-8', errors='ignore').splitlines()
                chunk_line = body_decoded[0]
                if chunk_line == '':
                    chunk_line = body_decoded[1]
                length = int(chunk_line.strip().split(';')[0], 16)
                chunk_line_len = len(chunk_line)
                if length == 0:
                    return result + body_bytes
                result += body_bytes[:length+chunk_line_len]
                avail_read = length + chunk_line_len - len(body_bytes[chunk_line_len:length+chunk_line_len])
                body_bytes = body_bytes[length+chunk_line_len:]
        return result

    def __close_conn(self, target_host_socket):
        """
        Close target and client connections
        :param target_host_socket:
        :return:
        """
        self.__client.close()
        target_host_socket.close()
        logging.info("Client <> Target closed")
