import datetime
import json
import os

from src.hotpot.app import Hotpot
from src.hotpot.wrappers import JSONResponse, Request
from src.hotpot.utils import redirect, generate_security_key, StyledJSON
from src.hotpot.exceptions import NotFound

app = Hotpot()


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
    return {}


@app.route("/user_info")
def user_info(_app: 'Hotpot', request: Request):
    return {}


@app.view_exception_404()
def view_exception_404(_app, error):
    return JSONResponse(StyledJSON(code=404, message="not found"))


if __name__ == "__main__":
    app.run()
