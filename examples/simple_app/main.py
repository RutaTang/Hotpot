import datetime
import json
import os

from src.hotpot.app import Hotpot
from src.hotpot.wrappers import JSONResponse, Request
from src.hotpot.utils import redirect, generate_security_key, StyledJSON
from src.hotpot.exceptions import NotFound

app = Hotpot()
app.app_global.db = "db"


# you can change hostname,port,debug mode, even security_key,by add them to config
# app.add_config({
#     "hostname": "localhost",
#     "port": 8080,
#     "debug": False,
#     "security_key": generate_security_key()
# })

@app.route("/")
def home(_app: 'Hotpot', request: Request):
    json_object = {
        "Home": "This is a home page"
    }
    return json_object


@app.route("/get_token")
def get_token(_app: 'Hotpot', request: Request):
    """
    get token which is used to access data
    """
    return {}


@app.route("/user_info")
def user_info(_app: 'Hotpot', request: Request):
    return {}


@app.route("/help")
def help(_app, request):
    return _app.api_help_doc


if __name__ == "__main__":
    app.run()
