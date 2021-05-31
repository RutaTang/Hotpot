from src.hotpot import Hotpot, Request
from sqlalchemy.engine import Connection
from sqlalchemy import text

bp = Hotpot(base_rule="/v1/")


@bp.route("/articles")
def articles(_app: 'Hotpot', request: Request):
    with _app.app_global.engine.connect() as conn:  # type: Connection
        result = conn.execute(text("select * from article;"))
        print(result.all())
    return {}


@bp.route("/help_doc")
def help_doc(_app: 'Hotpot', request: Request):
    return _app.api_help_doc()
