import datetime
import json
import os

from src.hotpot.app import Hotpot
from src.hotpot.wrappers import Response, Request
from src.hotpot.utils import redirect, generate_security_key
from src.hotpot.exceptions import NotFound, HTTPException, make_json_http_exception, MethodNotAllowed
from src.hotpot.globals import request, current_app, g

app = Hotpot(main_app=True)


# you can change hostname,port,debug mode, even security_key,by add them to config
# app.add_config({
#     "hostname": "localhost",
#     "port": 8080,
#     "debug": False,
#     "security_key": generate_security_key()
# })


@app.route("/")
@app.route("/index/")
def home():
    json_object = {
        "Home": "This is a home page"
    }
    return json_object


@app.route(r"/<regex('\d?'):phone>")
def regex(phone):
    print(phone)
    return {"regex": True}


@app.route("/get_token")
def get_token():
    """
    get token which is used to access data
    """
    print("enter")
    return {}


@app.route("/user_info")
def user_info():
    return {}


if __name__ == "__main__":
    app.run()
