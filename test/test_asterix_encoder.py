import unittest

from .testing_data import TEST_CAT001, TEST_CAT001_B, TEST_CAT034, TEST_CAT034_B, TEST_CAT048, TEST_CAT048_B
from asterix4py.AsterixEncoder import AsterixEncoder



class TestAsterixEncoder(unittest.TestCase):

    def test_cat048(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=TEST_CAT048
        )
        self.assertEqual(bytes(asterix_encoder.get_result()), TEST_CAT048_B)

    def test_cat034(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=TEST_CAT034
        )
        self.assertEqual(bytes(asterix_encoder.get_result()), TEST_CAT034_B)

    def test_cat001(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=TEST_CAT001
        )
        self.assertEqual(bytes(asterix_encoder.get_result()), TEST_CAT001_B)