import json

from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase


class Request(RequestBase):
    pass


class JSONResponse(ResponseBase):
    """
    Especially for JSON Response which is also only one supported in this WebFramework:
    Ex.
    JSONResponse({"Name":"Ruta"})
    """

    default_mimetype = "application/json"

    def __init__(self, json_object, **kwargs):
        json_str = json.dumps(json_object)
        super(JSONResponse, self).__init__(response=json_str, **kwargs)
