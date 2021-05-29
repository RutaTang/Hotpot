"""
Auth Utils Model for Restful authentication
"""
import json
from typing import Union

from cryptography import fernet

SECURITY_KEY = fernet.Fernet.generate_key()


class Token(object):
    """
    Auth through Token
    """

    def __init__(self, security_key: Union[bytes, str]):
        if isinstance(security_key, str):
            security_key = bytes(security_key, 'utf-8')
        self.security_key = security_key
        self.f = fernet.Fernet(self.security_key)

    def get_token(self, data: dict) -> str:
        data = bytes(json.dumps(data), 'utf-8')
        token = self.f.encrypt(data)
        token = str(token, 'utf-8')
        return token

    def get_data(self, token: Union[str, bytes]) -> dict:
        if isinstance(token, str):
            token = bytes(token, 'utf-8')
        data = self.f.decrypt(token)
        data = json.loads(data)
        return data

    def __call__(self, data_or_token: Union[dict, str, bytes]):
        if isinstance(data_or_token,dict):
            return self.get_token(data_or_token)
        elif isinstance(data_or_token, str) or isinstance(data_or_token, bytes):
            return self.get_data(data_or_token)
        else:
            raise TypeError("data_or_token should be dict,str,or bytes")