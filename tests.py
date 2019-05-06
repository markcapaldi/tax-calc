#!/usr/bin/python3

import unittest
import json

from unittest.mock import patch, mock_open

from CalculateTax import IncomeTaxData
from defaults import DEFAULT_DATA


class TestIncomeTaxData(unittest.TestCase):

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(DEFAULT_DATA)
    )
    def test_init_valid_json(self, mock_file):
        year = 2016
        year_data = IncomeTaxData(year)
        self.assertEqual(
            year_data.personal_allowance,
            DEFAULT_DATA[year]['personal_allowance']
        )
        self.assertEqual(
            year_data.starter_rate,
            DEFAULT_DATA[year]['starter_rate']
        )
        self.assertEqual(
            year_data.basic_rate.__dict__(),
            DEFAULT_DATA[year]['basic_rate']
        )
        self.assertEqual(
            year_data.intermediate_rate,
            DEFAULT_DATA[year]['intermediate_rate']
        )
        self.assertEqual(
            year_data.higher_rate.__dict__(),
            DEFAULT_DATA[year]['higher_rate']
        )
        self.assertEqual(
            year_data.top_rate,
            DEFAULT_DATA[year]['top_rate']
        )


if __name__ == '__main__':
    unittest.main()
