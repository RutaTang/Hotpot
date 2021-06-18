from werkzeug.local import Local, LocalProxy, release_local

from .globals import _local
from .wrappers import Request


class RequestContext(object):
    def __init__(self,environ,current_app):
        self.environ = environ
        self.current_app = current_app
        self._local = _local

    def __enter__(self):
        self._local.g = {}
        self._local.request = Request(environ=self.environ)
        self._local.current_app = self.current_app
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        release_local(_local)
