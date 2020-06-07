from proxy_server import ProxyServer


def main():
    """Init and run HttpServer"""
    server = ProxyServer("config.json")
    server.run()


if __name__ == '__main__':
    main()
