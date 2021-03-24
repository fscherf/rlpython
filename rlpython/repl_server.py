import threading
import socket

from rlpython.repl_connection import ReplConnection
from rlpython.repl import Repl


class ReplServer:
    def __init__(self, host='localhost', port=0,
                 repl_domain=Repl.DOMAIN.NETWORK, **repl_kwargs):

        self.host = host
        self.port = port
        self.repl_domain = repl_domain
        self.repl_kwargs = repl_kwargs

    def setup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

    def shutdown(self):
        self._running = False

    def __enter__(self):
        self.setup()
        self.run_multi_session(**self.repl_kwargs)

        return self

    def __exit__(self, type, value, traceback):
        self.shutdown()

    def get_port(self):
        return self.sock.getsockname()[1]

    def run_single_session(self, **repl_kwargs):
        repl_connection = None

        repl_kwargs = {
            **self.repl_kwargs,
            **repl_kwargs,
        }

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

    def run_multi_session(self, **repl_kwargs):
        def _server_thread():
            while self._running:
                try:
                    connection, address = self.sock.accept()

                except(socket.timeout, OSError):
                    continue

                connection_count[0] += 1

                repl_connection = ReplConnection(
                    repl_server=self,
                    connection=connection,
                    address=address,
                    repl_domain=self.repl_domain,
                    **repl_kwargs,
                )

                threading.Thread(
                    name='rlpython REPL Session {}'.format(
                        connection_count[0],
                    ),
                    daemon=True,
                    target=repl_connection.run_single_threaded,
                ).start()

        repl_kwargs = {
            **self.repl_kwargs,
            **repl_kwargs,
        }

        self.sock.settimeout(1)
        self._running = True

        connection_count = [0]

        threading.Thread(
            name='rlpython REPL Server',
            daemon=True,
            target=_server_thread,
        ).start()
