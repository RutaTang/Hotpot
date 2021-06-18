from typing import Callable, Union, Iterable
import configparser
import base64

from werkzeug.serving import run_simple
from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from werkzeug.routing import Map, Rule, MapAdapter

from cryptography.fernet import Fernet

from .wrappers import Request, Response
from .utils import join_rules, RegexConverter
from .context import RequestContext
from .globals import request
from .exceptions import *


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
        self.view_functions = {}
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
        # request_response_end
        self._request_response_end = []
        # api help doc
        self._api_help_doc = {}
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
    def api_help_doc(self):
        return self._api_help_doc

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

    def request_response_end(self):
        """
        Run methods before the request-response end (or say, after call all methods in self._after_response)
        f has no parameters and return nothing

        @request_response_end()
        def request_response_end() -> None:

        Usage: e.g. close db connection
        :return:
        """

        def decorator(f):
            self._request_response_end.append(f)
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

        # combine self and other app view_functions together
        for function_name, view_function in other_app.view_functions.items():
            self.view_functions[function_name] = view_function

        # Note: Config will not be influenced or changed by combing other app
        # Same as: security_key,app_global,exception_all,exceptions

        # combine self and other del_app function together
        for f in other_app._del_app:
            self._del_app.append(f)

        # combine self and other before_response function together
        for f in other_app._after_response:
            self._after_response.append(f)

        # combine self and other _api_help_doc
        for rule, doc in other_app._api_help_doc.items():
            self._api_help_doc[join_rules(self.base_rule, rule)] = doc
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
            response_or_dict = self.view_functions[endpoint](**values)
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
            # before request_response end
            for f in self._request_response_end:
                f()
        return response(environ, start_response)

    def route(self, rule, endpoint: str = None, methods: Iterable[str] = ["GET"], **options):
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
        :param options:
        :return:
        """

        def decorator(f: Callable):
            _endpoint = endpoint
            _rule = join_rules(self.base_rule, rule)
            if _endpoint is None:
                _endpoint = str(id(f))
            self.view_functions[_endpoint] = f
            self.url_map.add(Rule(_rule, endpoint=_endpoint, methods=methods))

            # add to api help doc
            rule_description = f.__doc__
            if rule_description is None:
                rule_description = ""
            self._api_help_doc[join_rules(self.base_rule, rule)] = rule_description.strip()
            return f

        return decorator

    def init_default_rule_converters(self):
        """
        Init Some helpful Rule Converters
        e.g. RegexConverter
        :return:
        """
        self.url_map.converters['regex'] = RegexConverter  # Regex Converters: /<regex("[0-9]"):phone)>

    # -----------handle http exception Start-----------
    def view_exception_all(self):
        """
       set custom views for all http exceptions
       Ex.
       @app.view_exception_all()
       def view_exception_all(_app,error):
           if isinstance(error,NOT_FOUND):
                return JSONResponse({"Not_Found": 404})
           return JSONResponse({"": 000})
       :return:

       Note: if use this function, all other view exception will not work.
        """

        def decorator(f: Callable[['Hotpot', HTTPException], ResponseBase]):
            self.exception_all = f

        return decorator

    def view_exception(self, code):
        """
        set view for http 404
        Ex.
        @app.view_exception_404()
        def view_exception_404(_app,error):
            print(error)
            return JSONResponse({"HttpException": 404})
        :return:
        """

        def decorator(f: Callable[['Hotpot', HTTPException], ResponseBase]):
            if code not in (400, 401, 403, 404, 406, 410, 422, 500):
                raise ValueError(
                    f"http code {code} is not supported, please use view_exception_all to customize your view function for your http exceptions")
            self.exception_404 = f
            setattr(self, f"exception_{code}", f)

        return decorator

    # -----------handle http exception End-----------
