import unittest

from fish import add_fish_to_aquarium

class TestAddFishToAquarium(unittest.TestCase):
    def test_add_fish_to_aquarium_success(self):
        actual = add_fish_to_aquarium(fish_list=["shark", "tuna"])
        #expected = {"tank_a": ["rabbit"]}
        expected = {"tank_a": ["shark", "tuna"]}
        self.assertEqual(actual, expected)