#!/usr/bin/python3

import unittest
import json

from unittest.mock import patch, mock_open

from CalculateTax import IncomeTaxYearData
from defaults import DEFAULT_DATA


class TestIncomeTaxYearData(unittest.TestCase):

    def test_init_valid_json(self):
        year = 2016
        year_data = IncomeTaxYearData(DEFAULT_DATA[year], 30000)
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
        self.assertEqual(year_data.personal_allowance, 11000)

    def test_init_unexpected_valid_json(self):
        with self.assertLogs(level='ERROR') as cm:
            IncomeTaxYearData({'foo': 'bar'}, 30000)
        self.assertEqual(cm.output, [
            'ERROR:root:Personal Allowance data is missing or corrupt, please '
            'try reseting tax data using -r parameter.'
        ])


if __name__ == '__main__':
    unittest.main()
