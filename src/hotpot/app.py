import functools
import time

import json
import os
from typing import Callable, Union
from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.serving import run_simple
from werkzeug.routing import Map, Rule, MapAdapter
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect as werkzeug_redirect
from tinydb import TinyDB


class AppGlobal(dict):
    def __init__(self):
        super().__init__()

    def __getattribute__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


class Request(RequestBase):
    pass


class JSONResponse(ResponseBase):
    default_mimetype = "application/json"

    def __init__(self, json_object, **kwargs):
        json_str = json.dumps(json_object)
        super(JSONResponse, self).__init__(response=json_str, **kwargs)


def redirect(location, code=302):
    return werkzeug_redirect(location=location, code=code)


class Hotpot(object):
    """
    app = Hotpot()
    @app.route("/)
    def index(request,**values):
        return {"Example":True}
    """

    def __init__(self, config: dict):
        self.url_map = Map([])
        self.view_functions = {}
        self.config = config
        # init AppGlobal
        self._init_app_global()
        # Other methods need to run before app real end
        self._after_app_end = []
        # before_request
        self._before_request = []
        # after_request
        self._after_request = []

    # Decorator
    # @app.before_app_run
    def before_app(self):
        def decorator(f):
            f()
            return f

        return decorator

    def after_app(self):
        def decorator(f):
            self._after_app_end.append(f)
            return f

        return decorator

    def before_request(self):
        def decorator(f):
            self._before_request.append(f)
            return f

        return decorator

    def after_request(self):
        def decorator(f):
            self._after_request.append(f)
            return f

        return decorator

    def __del__(self):
        # run all methods which after app end
        for f in self._after_app_end:
            f()
        # del AppGlobal
        self._del_app_global()

    def _init_app_global(self):
        self.app_global = AppGlobal()

    def _del_app_global(self):
        del self.app_global

    def __call__(self, environ, start_response):
        # Request Start
        for f in self._before_request:
            f()
        wsgi_app_response = self.wsgi_app(environ=environ, start_response=start_response)
        # Request End
        for f in self._after_request:
            f()
        return wsgi_app_response

    def run(self, hostname='localhost', port=8080, debug=True):
        run_simple(hostname, port, self, use_reloader=debug, use_debugger=debug)

    def dispatch_request(self, request) -> Union[ResponseBase, HTTPException]:
        adapter = self.url_map.bind_to_environ(request.environ)  # type:MapAdapter
        try:
            endpoint, values = adapter.match()
            # route will return response or json dict
            # @app.route("/"
            # def index(request):
            #   return {"Name":""}
            #   #or
            #   return Response()
            response_or_dict = self.view_functions[endpoint](request, **values)
            if isinstance(response_or_dict, dict):
                return JSONResponse(response_or_dict)
            elif isinstance(response_or_dict, ResponseBase):
                return response_or_dict
            else:
                raise HTTPException("Service Error: Unsupported Response")
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request=request)
        return response(environ, start_response)

    def route(self, rule, **options):
        def decorator(f: Callable):
            self.view_functions[f.__name__] = f
            self.url_map.add(Rule(rule, endpoint=f.__name__))

        return decorator
