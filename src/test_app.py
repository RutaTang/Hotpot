import time
from unittest import TestCase
from hotpot.app import Hotpot,AppGlobal
from tinydb import TinyDB


class TestHotpot(TestCase):
    def setUp(self) -> None:
        self.app = Hotpot({})

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

