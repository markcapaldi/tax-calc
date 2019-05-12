#!/usr/bin/python3

import argparse
import json
import unittest


from CalculateTax import (
    IncomeTaxYearData,
    _validate_year,
    _validate_salary,
)
from defaults import DEFAULT_DATA, TAX_DATA_FILE_NAME


class TestUtilFunctions(unittest.TestCase):
    def test_validate_year_valid_year(self):
        year = 2012
        test_response = _validate_year(year)
        self.assertEqual(test_response, year)

    def test_validate_year_invalid_year(self):
        year = -500
        with self.assertRaises(argparse.ArgumentTypeError):
            _validate_year(year)

    def test_validate_year_very_invalid_year(self):
        year = 'foo'
        with self.assertRaises(ValueError):
            _validate_year(year)

    def test_validate_salary_valid_salary(self):
        salary = 40000
        test_response = _validate_salary(salary)
        self.assertEqual(test_response, salary)

    def test_validate_salary_invalid_salary(self):
        salary = -500
        with self.assertRaises(argparse.ArgumentTypeError):
            _validate_salary(salary)

    def test_validate_salary_very_invalid_salary(self):
        salary = 'foo'
        with self.assertRaises(ValueError):
            _validate_salary(salary)


class TestIncomeTaxYearData(unittest.TestCase):

    maxDiff = None

    # __init__ tests

    def test_init_valid_json_part_data(self):
        year = "2016"
        year_data = IncomeTaxYearData(DEFAULT_DATA.get(year), 30000)
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

    def test_init_valid_json_full_data(self):
        year = "2018"
        year_data = IncomeTaxYearData(DEFAULT_DATA.get(year), 30000)
        self.assertEqual(
            year_data.personal_allowance,
            DEFAULT_DATA[year]['personal_allowance']
        )
        self.assertEqual(
            year_data.starter_rate.__dict__(),
            DEFAULT_DATA[year]['starter_rate']
        )
        self.assertEqual(
            year_data.basic_rate.__dict__(),
            DEFAULT_DATA[year]['basic_rate']
        )
        self.assertEqual(
            year_data.intermediate_rate.__dict__(),
            DEFAULT_DATA[year]['intermediate_rate']
        )
        self.assertEqual(
            year_data.higher_rate.__dict__(),
            DEFAULT_DATA[year]['higher_rate']
        )
        self.assertEqual(
            year_data.top_rate.__dict__(),
            DEFAULT_DATA[year]['top_rate']
        )
        self.assertEqual(year_data.personal_allowance, 11850)

    def test_init_unexpected_valid_json(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData({'foo': 'bar'}, 30000)

        msg = ('Personal Allowance data is missing or corrupt, please '
               'try reseting tax data using -r parameter.')
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_year_tax_data_is_null(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData(None, 30000)
        msg = "year_tax_data can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_gross_salary_is_null(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData(2015, None)
        msg = "gross_salary can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    # Not implemented method test stubs

    def test_add_not_implemented(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        with self.assertRaises(NotImplementedError):
            year_data.add()

    def test_edit_not_implemented(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        with self.assertRaises(NotImplementedError):
            year_data.edit()

    def test_delete_not_implemented(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        with self.assertRaises(NotImplementedError):
            year_data.delete()

    def test_save_not_implemented(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        with self.assertRaises(NotImplementedError):
            year_data.save()

    # Label functions tests

    def test_get_gross_salary_label(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        label = year_data.get_gross_salary_label()
        self.assertEqual(label, 'Gross Salary: £30,000.00\n')

    def test_get_personal_allowance_label(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        label = year_data.get_personal_allowance_label()
        self.assertEqual(year_data.personal_allowance, 11000)
        self.assertEqual(label, 'Personal Allowance: £11,000.00\n')

    def test_get_taxable_income_label(self):
        year_data = IncomeTaxYearData(DEFAULT_DATA.get("2016"), 30000)
        label = year_data.get_taxable_income_label()
        self.assertEqual(label, 'Taxable Income: £19,000.00\n')

    # Various tests
    def test_load_json_file(self):
        IncomeTaxYearData._reset_tax_data()
        with open(TAX_DATA_FILE_NAME) as json_file:
            tax_data = json.load(json_file)
        self.assertEqual(tax_data, json.loads(json.dumps(DEFAULT_DATA)))


if __name__ == '__main__':
    unittest.main()
