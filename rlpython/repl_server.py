import socket

from rlpython.repl_connection import ReplConnection
from rlpython.repl import Repl


class ReplServer:
    def __init__(self, host='localhost', port=0,
                 repl_domain=Repl.DOMAIN.NETWORK):

        self.host = host
        self.port = port
        self.repl_domain = repl_domain

    def setup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

    def shutdown(self):
        pass

    def get_port(self):
        return self.sock.getsockname()[1]

    def run_single_threaded(self, **repl_kwargs):
        repl_connection = None

        try:
            connection, address = self.sock.accept()

            repl_connection = ReplConnection(
                repl_server=self,
                connection=connection,
                address=address,
                repl_domain=self.repl_domain,
                **repl_kwargs,
            )

            repl_connection.run_single_threaded()

        except KeyboardInterrupt:
            return

        finally:
            if repl_connection:
                repl_connection.shutdown()
