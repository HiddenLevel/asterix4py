import copy
import unittest

from asterix4py.AsterixParser import AsterixParser

from .testing_data import TEST_CAT001, TEST_CAT001_B, TEST_CAT034, TEST_CAT034_B, TEST_CAT048, TEST_CAT048_B
from asterix4py.AsterixEncoder import AsterixEncoder


class TestAsterixEncoder(unittest.TestCase):

    def test_cat048(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=copy.deepcopy(TEST_CAT048)
        )
        self.assertEqual(bytes(asterix_encoder.get_result()), TEST_CAT048_B)

    def test_cat048_encode_decode(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=copy.deepcopy(TEST_CAT048)
        )

        asterix_parser = AsterixParser(
            bytes(asterix_encoder.get_result())
        )

        asterix_encoder_b = AsterixEncoder(
            asterix_msg=asterix_parser.get_result()[1]
        )
        self.assertEqual(bytes(asterix_encoder_b.get_result()), TEST_CAT048_B)

    def test_cat034(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=copy.deepcopy(TEST_CAT034)
        )
        self.assertEqual(bytes(asterix_encoder.get_result()), TEST_CAT034_B)

    def test_cat034_encode_decode(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=copy.deepcopy(TEST_CAT034)
        )

        asterix_parser = AsterixParser(
            bytes(asterix_encoder.get_result())
        )

        asterix_encoder_b = AsterixEncoder(
            asterix_msg=asterix_parser.get_result()[1]
        )
        self.assertEqual(bytes(asterix_encoder_b.get_result()), TEST_CAT034_B)

    def test_cat001(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=copy.deepcopy(TEST_CAT001)
        )
        self.assertEqual(bytes(asterix_encoder.get_result()), TEST_CAT001_B)

    def test_cat001_encode_decode(self):
        asterix_encoder = AsterixEncoder(
            asterix_msg=copy.deepcopy(TEST_CAT001)
        )

        asterix_parser = AsterixParser(
            bytes(asterix_encoder.get_result())
        )

        asterix_encoder_b = AsterixEncoder(
            asterix_msg=asterix_parser.get_result()[1]
        )
        self.assertEqual(bytes(asterix_encoder_b.get_result()), TEST_CAT001_B)
