from src.hotpot import Hotpot, Request

bp = Hotpot()


@bp.route("/articles")
def articles(_app: 'Hotpot', request: Request):
    return {}

