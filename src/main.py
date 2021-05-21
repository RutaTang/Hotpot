import json

from hotpot.app import Hotpot, JSONResponse, redirect
from tinydb import TinyDB
from werkzeug.serving import run_simple

app = Hotpot(config={})


@app.before_app()
def init_db():
    pass


@app.after_app()
def del_db():
    pass


@app.route("/")
def index(request):
    json_object = {
        "Name": "Ruta",
        "Age": 18,
    }
    return json_object


@app.route("/count")
def count(request):
    return {}


@app.route("/article")
def article(request):
    return redirect(location="/")

# app.run(debug=True)
