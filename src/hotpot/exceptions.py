from werkzeug.exceptions import *

from .wrappers import Response


def make_json_http_exception(exception: HTTPException):
    """
    Make Werkzeug.exception to json exception
    :param exception:
    :return:
    """
    exception.response = Response(json_object={"code": exception.code, "description":exception.description})
    return exception
