import unittest

from s import add


class TestAdd(unittest.TestCase):
    def test_add(self):
        actual = add(1, 2)
        expected = 3
        self.assertEqual(actual, expected)
