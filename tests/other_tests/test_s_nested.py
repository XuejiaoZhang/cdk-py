import unittest

from s_nested import add_nested_s


class TestAddNested(unittest.TestCase):
    def test_add_nested_s(self):
        actual = add_nested_s(1, 2, 3)
        expected = 6
        self.assertEqual(actual, expected)
