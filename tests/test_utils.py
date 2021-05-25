import os.path
from unittest import TestCase
from src.hotpot.utils import join_rules
class TestUtils(TestCase):

    def test_join_rules(self):

        print(join_rules("","auth/","/name/info//s"))
