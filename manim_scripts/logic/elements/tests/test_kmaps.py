# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Unittest some helper methods in KMaps.py
"""

__author__ = "Kyle Vitautas Lopin"


import unittest
from manim_scripts.logic.elements.KMaps import KarnaughMap


class Dummy:
    num_vars = 3
    var_names = ["A", "B", "C"]
    term_to_minterms = KarnaughMap.term_to_minterms


class TestTermToMinterms(unittest.TestCase):
    def setUp(self):
        self.d = Dummy()

    def test_ab(self):
        self.assertEqual(self.d.term_to_minterms("AB"), [6, 7])

    def test_a_not_b_not(self):
        self.assertEqual(self.d.term_to_minterms("A'B'"), [0, 1])


if __name__ == "__main__":
    unittest.main()
