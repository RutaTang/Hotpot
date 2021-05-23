from hotpot.app import Hotpot
from hotpot.utils import login_required,redirect
app = Hotpot()


@app.route("/from_other_app")
def index_from_other_app(_app:'Hotpot', requst):
    return {"Index": "From Other App"}
