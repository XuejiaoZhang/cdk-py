import unittest

from r import deduct


class TestDeduct(unittest.TestCase):
    def test_deduct(self):
        actual = deduct(2, 1)
        expected = 1
        self.assertEqual(actual, expected)
