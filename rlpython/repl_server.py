import threading
import socket
import os

from rlpython.repl_connection import ReplConnection
from rlpython.utils.url import parse_url
from rlpython.repl import Repl


class ReplServer:
    def __init__(self, url, permissions, repl_domain=Repl.DOMAIN.NETWORK,
                 print=print, **repl_kwargs):

        self.url = url
        self.permissions = permissions
        self.repl_domain = repl_domain
        self._print = print
        self.repl_kwargs = repl_kwargs

        self.scheme, self.host, self.port = parse_url(url)

        # setup for local networking
        if(self.scheme == 'file' or
           self.host in ('127.0.0.1', 'localhost', '::')):

            self.repl_domain = Repl.DOMAIN.LOCAL_NETWORK

    def setup(self):
        # network
        if self.scheme == 'rlpython':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bind_arg = (self.host, self.port)

        # unix domain socket
        elif self.scheme == 'file':
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            bind_arg = self.host

            try:
                os.remove(self.host)

            except OSError:
                pass

        self.sock.bind(bind_arg)

        if self.scheme == 'file':
            # set file permmisions
            os.chmod(self.host, int(self.permissions, 8))

        self.sock.listen(1)

    def print_bind_informations(self):
        if not self._print:
            return

        if self.scheme == 'rlpython':
            sock_name = self.sock.getsockname()

            self._print(
                'rlpython: running on {}:{}'.format(
                    sock_name[0],
                    sock_name[1],
                )
            )

        elif self.scheme == 'file':
            self._print(
                'rlpython: running on file://{}'.format(self.host),
            )

    def shutdown(self):
        self._running = False

        # remove unix domain socket
        if self.scheme == 'file':
            try:
                os.remove(self.host)

            except OSError:
                pass

    def __enter__(self):
        self.setup()
        self.print_bind_informations()
        self.run_multi_session(**self.repl_kwargs)

        return self

    def __exit__(self, type, value, traceback):
        self.shutdown()

    def get_host(self):
        return self.sock.getsockname()[0]

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
