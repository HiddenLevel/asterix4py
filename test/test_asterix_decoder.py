import unittest

from asterix4py.AsterixParser import AsterixParser

from .testing_data import TEST_CAT001, TEST_CAT001_B, TEST_CAT034, TEST_CAT034_B, TEST_CAT048, TEST_CAT048_B

class TestAsterixParser(unittest.TestCase):

    def test_cat048(self):
        self.maxDiff = None
        asterix_parser = AsterixParser(
            bytesdata=TEST_CAT048_B
        )

        self.assertDictEqual(
            asterix_parser.get_result()[1],
            TEST_CAT048
        )

    def test_cat034(self):
        asterix_parser = AsterixParser(
            bytesdata=TEST_CAT034_B
        )

        self.assertDictEqual(
            asterix_parser.get_result()[1],
            TEST_CAT034
        )

    def test_cat001(self):
        asterix_parser = AsterixParser(
            bytesdata=TEST_CAT001_B
        )

        self.assertDictEqual(
            asterix_parser.get_result()[1],
            TEST_CAT001
        )