import logging
import signal
import sys
from socket import SOCK_STREAM, socket, AF_INET, timeout

from proxy_passer import ProxyPasser
from request_parser import RequestParser

from response_parser import ResponseParser
from server_config import ServerConfig
from thread_pool import ThreadPool


class ProxyServer:
    __request_parser: RequestParser = RequestParser()
    __response_parser: ResponseParser = ResponseParser()

    def __init__(self, config_name="config.json"):
        self.__config = ServerConfig(config_name)
        logging.basicConfig(filename=self.__config.log_file,
                            level=logging.DEBUG,
                            format='%(asctime)s %(message)s')
        self.thread_pool = ThreadPool()

    def run(self):
        """Binds, listens, processing HTTP requests on socket"""
        signal.signal(signal.SIGINT, self.__handle_exit)
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((self.__config.host, self.__config.port))
        s.listen(self.__config.queue_size)
        logging.info(f'Launched at {self.__config.port}')
        while True:
            try:
                client_connection, _ = s.accept()
            except SystemExit as e:
                s.close()
                break
            except Exception as e:
                logging.info(e)
                s.close()
                break
           # client_connection.settimeout(self.__config.max_req_time)
            self.thread_pool.add_task(self.__route_request, client_connection)

    def __route_request(self, client):
        """Routes request to handler if exists, then closes the connection"""
        proxy_passer = ProxyPasser(client)
        proxy_passer.run()

    def __read_from_socket(self, sock, is_response):
        """Reads request data from socket. If request method or protocol
        are not supported, rejects it"""
        result = bytearray()
        headers = None
        head_len = 0
        total_len = None
        while not total_len or head_len < total_len:
            chunk = sock.recv(8192)
            if not chunk:
                break
            result += chunk
            head_len += len(chunk)
            if not headers:
                headers = self.try_get_headers(result, is_response)
                if not headers:
                    continue
            total_len_raw = headers.get("Content-Length")
            if total_len_raw:
                total_len = int(total_len_raw)
            else:
                continue
        return result

    def try_get_headers(self, data, is_response):
        try:
            if is_response:
                headers, parsed_msg = self.__response_parser.parse(data)
            else:
                headers, parsed_msg = self.__request_parser.parse(data)
            if parsed_msg:
                return headers
        except ValueError:
            return None

    def __handle_exit(self, signal, frame):
        logging.info("Received SIGINT, shutting down threads...")
        print("shutting down...")
        self.thread_pool.tasks.join()
        self.thread_pool.terminate_all_workers()
        logging.info("Threads stopped")
        sys.exit(0)


class ReadSocketError(Exception):
    """Error indicating there was some issues reading from the socket."""
    pass
