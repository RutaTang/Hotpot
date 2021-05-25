from hotpot.app import Hotpot
from hotpot.utils import login_required, redirect

app = Hotpot(main_app=False,base_rule="/other_app/",name="other_app")


@app.route("/index")
def index(_app: 'Hotpot', request):
    return {"Index": "From Other App"}
