from typing import Callable, Union, Iterable, ClassVar, Type
from types import FunctionType
from abc import ABC, abstractmethod
import configparser
import base64
import inspect

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.routing import Map, Rule, MapAdapter

from cryptography.fernet import Fernet

from .wrappers import Request, Response
from .utils import join_rules, RegexConverter
from .context import RequestContext
from .globals import request
from .exceptions import *


class Resource(ABC):
    @classmethod
    def __are_methods_implemented(cls, methods: [str]):
        """
        Check whether Resource implement all corresponding methods with function name in lower letter, e.g. def get(self)
        :param methods: [str], e.g. ["GET","POST"]
        :return:
        """
        for method in methods:
            if not hasattr(cls, method.lower()):
                raise NotImplementedError(f"corresponding http methods {methods} should be implemented")

    @classmethod
    def are_methods_implemented(cls, methods: [str]):
        cls.__are_methods_implemented(methods)


class Hotpot(object):
    """
    This is the core part of the web framework.
    WSGI Server will call the instance of this Class to process request.

    Ex.
    app = Hotpot(config={})
    @app.route("/)
    def index(request,**values):
        return {"Example":True}
    """

    def __init__(self, main_app=False, base_rule="/"):
        self.url_map = Map([])
        self.view_functions_info = {}
        self.config = {
            # Default Config
            "hostname": 'localhost',
            "port": 8080,
            "debug": True,
            # security key for session
            "security_key": b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls=',
        }
        # main_app for checking whether the app is considered as main app or combined to the main app
        self.main_app = main_app
        # base_rule
        self.base_rule = base_rule
        # security key for session ref to config['security_key']
        self.security_key = self.config.get("security_key", b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls=')
        # after_app
        self._del_app = []
        # before_request
        self._before_request = []
        # after_response
        self._after_response = []
        # whether automatically change normal exception to json exception
        self.json_exception = True

        # other init functions
        self.init_default_rule_converters()  # init default Rule Converter

    def __del__(self):
        # run all methods which after app end
        if self.main_app:
            for f in self._del_app:
                f(self)

    def __call__(self, environ, start_response):
        wsgi_app_response = self.wsgi_app(environ=environ, start_response=start_response)
        return wsgi_app_response

    # -------------Decorator Begin-------------
    # TODO: review, redesign, and recode hooks
    def hook_del_app(self):
        """
        Run methods as app del
        :return:
        """

        def decorator(f):
            self._del_app.append(f)
            return f

        return decorator

    def before_request(self):
        """
        Run methods before each request is really dispatched;
        global request, current_app, and g can be accessed now
        f has no parameters and return

        Ex.
        @before_request()
        def before_request() -> None:

        Usage: e.g. connect db
        :return:
        """

        def decorator(f):
            self._before_request.append(f)
            return f

        return decorator

    def after_response(self):
        """
        Run methods after each response made but before return to the client
        f must have a parameter position to get response and return a response: f(response) -> ResponseBase
        Ex.
        @after_response()
        def after_response(response) -> ResponseBase:

        :return:
        """

        def decorator(f):
            self._after_response.append(f)
            return f

        return decorator

    # -------------Decorator End -------------
    def combine_app(self, other_app: 'Hotpot'):
        # combine self and other app url_map together
        for endpoint, rule_list in other_app.url_map._rules_by_endpoint.items():
            rule = rule_list[0]  # type:Rule
            rule_path = rule.rule
            if self.base_rule == "/":
                self.url_map.add(rule.empty())
            else:
                self.url_map.add(Rule(join_rules(self.base_rule, rule_path), endpoint=endpoint))

        # combine self and other app view_functions_info together
        for endpoint, info in other_app.view_functions_info.items():
            self.view_functions_info[endpoint] = info

        # Note: Config will not be influenced or changed by combing other app
        # Same as: security_key,app_global,exception_all,exceptions

        # combine self and other del_app function together
        for f in other_app._del_app:
            self._del_app.append(f)

        # combine self and other _before_request function together
        for f in other_app._before_request:
            self._before_request.append(f)

        # combine self and other before_response function together
        for f in other_app._after_response:
            self._after_response.append(f)

        # Finally Del the other app
        del other_app

    def set_config(self, config: Union[dict, str]):
        """
        Set self.config
        :param config: dict or str; if str, it should be a path.
        :return:
        """
        if isinstance(config, dict):
            self.config = config
        elif isinstance(config, str):
            config_parser = configparser.ConfigParser()
            config_parser.read(config)
            self.config = config_parser._sections
        else:
            raise TypeError("config should be dict or str (path)")
        # reload config
        self.security_key = self.config.get("security_key", b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls=')

    def run(self):
        """
        Simple WSGI Server for development other than production
        :return:
        """

        # if self is not main app, not allowed to run
        if not self.main_app:
            raise RuntimeError("App with that main_app is False is not allowed to run!")
        hostname = self.config.get("hostname", "localhost")
        port = self.config.get("port", 8080)
        debug = self.config.get("debug", True)
        run_simple(hostname, port, self, use_reloader=debug, use_debugger=debug)

    def dispatch_request(self) -> Union[ResponseBase, HTTPException]:
        adapter = self.url_map.bind_to_environ(request.environ)  # type:MapAdapter
        try:
            endpoint, values = adapter.match()
            # route will return response or json dict
            # @app.route("/"
            # def index(request):
            #   return {"Name":""}
            #   #or
            #   return Response()
            view_function_info = self.view_functions_info[endpoint]
            view_function = view_function_info['f']
            if inspect.isclass(view_function) and issubclass(view_function,
                                                             Resource):  # For View Class of SubClass Of Resource
                init_args = view_function_info['args']
                init_kwargs = view_function_info['kwargs']
                view_function = view_function(*init_args, **init_kwargs)
                view_function = getattr(view_function, request.method.lower())
            response_or_dict = view_function(**values)
            if isinstance(response_or_dict, dict):
                return Response(response_or_dict)
            elif isinstance(response_or_dict, ResponseBase):
                return response_or_dict
            else:
                raise RuntimeError("Server App Error: Unsupported Response")
        except HTTPException as e:
            # whether automatically makes all http exception in the json format
            if self.json_exception:
                return make_json_http_exception(e)
            else:
                return e

    def wsgi_app(self, environ, start_response):
        with RequestContext(environ, self):
            # before each request
            for f in self._before_request:
                f()
            response = self.dispatch_request()
            # after make response, customize response generally
            for f in self._after_response:
                response = f(response)
        return response(environ, start_response)

    def route(self, rule, endpoint: str = None, methods: Iterable[str] = ["GET"], class_init_args=[],
              class_init_kwargs: dict = {},
              **options):
        """
        Map url path to view functions (or say endpoints)
        Ex.
        @route("/")
        @route("/index") # you can do this, / and /index, both work
        def index():
            return {}

        !!!Important Note:
        (1) if two or more routes have same rule, say "/", but different endpoint name, the first defined Rule will be called
        (2) if two or more routes have same rule and same endpoint name, the last defined Rule will be called
        :param rule: url path, like "/"
        :param endpoint: explicitly set endpoint, or it will be function name
        :param methods: allowed http methods, default just allow "GET"
        :param class_init_args: arguments when init Resource, only for Resource Class,
        :param class_init_kwargs: arguments when init Resource, only for Resource Class
        :param options:
        :return:
        """

        def decorator(f: Union[FunctionType, Resource, Type[Resource]]):
            _endpoint = endpoint
            _rule = join_rules(self.base_rule, rule)
            if _endpoint is None:
                _endpoint = str(id(f))
            if inspect.isclass(f) and issubclass(f, Resource):
                f.are_methods_implemented(methods=methods)  # check whether all http methods implemented
            elif inspect.isfunction(f):
                pass
            else:
                raise TypeError("view function should be a function or a subclass of Resource")
            self.url_map.add(Rule(_rule, endpoint=_endpoint, methods=methods))
            self.view_functions_info[_endpoint] = {"f": f, "args": class_init_args, "kwargs": class_init_kwargs}
            return f

        return decorator

    def init_default_rule_converters(self):
        """
        Init Some helpful Rule Converters
        e.g. RegexConverter
        :return:
        """
        self.url_map.converters['regex'] = RegexConverter  # Regex Converters: /<regex("[0-9]"):phone)>
