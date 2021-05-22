import time
from unittest import TestCase
from hotpot.app import Hotpot,AppGlobal
from hotpot.sessions import set_session
from tinydb import TinyDB



class TestHotpot(TestCase):
    def setUp(self) -> None:
        self.app = Hotpot()

    def test__get_db(self):
        db = TinyDB("./default.json")
        table = db.table("name")
        table.insert({"Name": "Ruta"})
        print("Ok")
        time.sleep(5)
        print(table.all())
        db.close()

    def test_g(self):
        ag = AppGlobal()

    def test_config(self):
        self.app.add_config(config="./example.ini")

    def test_set_session(self):
        a,b = [1,2]
        import base64
        from cryptography.fernet import Fernet
        x = b'YgHfXTZRK1t_tTGOh139WEpEii5gkqobuD89U7er1Ls='
        print(len(x))
