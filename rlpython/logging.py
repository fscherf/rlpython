import logging
import os


class SilentLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def _debug_enabled(self):
        value = os.environ.get('RLPYTHON_DEBUG', '').strip().lower()

        return value in ('1', 'enabled', 'enable', 'true')

    def debug(self, *args, **kwargs):
        if not self._debug_enabled():
            return

        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)
