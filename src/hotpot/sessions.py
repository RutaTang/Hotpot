from werkzeug.wrappers import Response as ResponseBase, Request as RequestBase
from cryptography.fernet import Fernet, InvalidToken, InvalidSignature

KEY_NAME = "hotpot"


def set_session(content: dict, response: ResponseBase, security_key: bytes):
    content_str = ""
    for k, v in content.items():
        content_str += f"{k}={v};"
    f = Fernet(security_key)
    token = f.encrypt(bytes(content_str, "utf-8"))
    response.set_cookie(KEY_NAME, token)


def get_session(request: RequestBase, security_key: bytes):
    session_from_cookie = request.cookies.get(KEY_NAME, default=None)
    if session_from_cookie is None:
        return {}
    f = Fernet(security_key)
    try:
        session_info = f.decrypt(bytes(session_from_cookie, 'utf-8')).decode("utf-8")
    except InvalidToken:
        return {}

    def convert_str_to_dict(session_info: str):
        session_array = session_info.split(';')
        session_dict = {}
        for i, item in enumerate(session_array):
            kv = session_array[i].strip()
            if len(kv) == 0:
                continue
            k, v = kv.split('=')
            session_dict[str(k)] = str(v)
        return session_dict

    session_dict = convert_str_to_dict(session_info)

    return session_dict


def clear_session(response: ResponseBase):
    response.delete_cookie(KEY_NAME)
