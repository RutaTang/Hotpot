import json
import os

from src.hotpot.app import Hotpot
from src.hotpot.wrappers import JSONResponse, Request
from src.hotpot.utils import redirect, login_required, login as login_, logout as logout_, generate_security_key
from src.hotpot.sessions import set_session, get_session, clear_session

app = Hotpot()

# you can change hostname,port,debug mode, even security_key,by add them to config
# app.add_config({
#     "hostname": "localhost",
#     "port": 8080,
#     "debug": False,
#     "security_key": generate_security_key()
# })

@app.after_app()
def after_app_f01(_app:Hotpot):
    app.app_global.db.close()

@app.route("/")
def home(_app: 'Hotpot', request: Request):
    json_object = {
        "Home": "This is a home page"
    }
    return json_object


@app.view_exception_404()
def view_exception_404(_app, error):
    return JSONResponse({"HttpException": 404})


if __name__ == "__main__":
    app.run()
