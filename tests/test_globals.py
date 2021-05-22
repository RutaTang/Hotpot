from unittest import TestCase
from src.hotpot.globals import AppGlobal


class TestAppGlobal(TestCase):
    def setUp(self) -> None:
        self.app_global = AppGlobal()

    def test_get_set_attribute_dot(self):
        self.app_global.x = 1
        self.assertEqual(1,self.app_global.x)

    def test_get_set_attribute_bracket(self):
        self.app_global['y'] = 1
        self.assertEqual(1,self.app_global['y'])

    def test_get_set_attribute_mix(self):
        self.app_global.z = 1
        self.assertEqual(1,self.app_global['z'])
        self.app_global['g'] = 1
        self.assertEqual(1,self.app_global.g)