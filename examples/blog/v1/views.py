import jwt

from src.hotpot import Hotpot, Request, StyledJSON, NotFound, BadRequest, Unauthorized,InternalServerError

from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy import text, select, delete
from sqlalchemy.orm import Session

from .models import Article, User

bp = Hotpot(base_rule="/v1/")


@bp.route("/get_token")
def get_token(_app: 'Hotpot', request: Request):
    """
    Get Token
    """
    if request.method == "POST":
        username = request.form.get("username", None)
        pwd = request.form.get("pwd", None)
        if username is None or pwd is None:
            raise BadRequest()
        with Session(_app.app_global.engine) as session:  # type: Connection
            results = session.execute(
                select(User).where(User.username == username, User.pwd == pwd))  # type:CursorResult
            user = results.fetchone()
            if user is None:
                raise NotFound()
            user = user[0]
            token = jwt.encode({"id": user.id, "is_superuser": user.is_superuser}, _app.security_key)
            return StyledJSON(data={"token": token})
    else:
        raise BadRequest()


@bp.route("/articles")
def articles(_app: 'Hotpot', request: Request):
    """
    Get Articles
    Usage:
    GET /articles, /articles?id=1
    DELETE /articles?id=1
    """
    if request.method == "GET":
        # No Authentication needed
        article_id = request.args.get("id", None)
        # Query articles
        with Session(_app.app_global.engine) as session:
            query_exp = select(Article)
            if article_id is not None:
                query_exp = select(Article).where(Article.id == article_id)
            result = session.execute(query_exp)
            result_array = []
            for article_object in result.scalars():  # type: Article
                result_array.append(article_object.json())
        return StyledJSON(data=result_array, type="Article")
    elif request.method == "DELETE":
        # Authentication needed
        token = request.form.get("token", None)
        if token is None:
            raise Unauthorized()
        data_from_token = jwt.decode(token, _app.security_key, algorithms=['HS256'])
        is_superuser = data_from_token.get("is_superuser",None)
        if is_superuser is None:
            raise InternalServerError()
        if not is_superuser:
            raise Unauthorized()
        # query id
        article_id = request.args.get("id",None)
        if article_id is None:
            raise BadRequest()
        with Session(_app.app_global.engine) as session:
            article = session.query(Article).filter(Article.id == article_id).first()
            if article is None:
                raise NotFound()
            session.delete(article)
            session.commit()
        return StyledJSON(message="Delete Successful",data={})
    raise BadRequest()


@bp.route("/help_doc")
def help_doc(_app: 'Hotpot', request: Request):
    return _app.api_help_doc()
