#!/usr/bin/python3

import argparse
import json
import unittest


from CalculateTax import (
    _validate_salary,
    _validate_year,
    IncomeTaxYearData,
    TaxBand,
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
        with self.assertRaises(argparse.ArgumentTypeError):
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
        with self.assertRaises(argparse.ArgumentTypeError):
            _validate_salary(salary)


class TestIncomeTaxYearData(unittest.TestCase):

    maxDiff = None

    # __init__ tests

    def test_init_valid_json_part_data(self):
        year = "2016"
        year_data = IncomeTaxYearData(
            year=year,
            tax_data=DEFAULT_DATA,
            gross_salary=30000
        )
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

    def test_init_valid_json_part_data_as_str(self):
        year = "2016"
        year_data = IncomeTaxYearData(
            year=year,
            tax_data=json.dumps(DEFAULT_DATA),
            gross_salary=30000
        )
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

    def test_init_valid_json_part_data_bad_data(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData(
                year="2016",
                tax_data={"2016": {
                    'starter_rate': None,
                    'basic_rate': {
                        'rate': 20,
                        'range_start': 0,
                        'range_end': 32000
                    },
                    'intermediate_rate': None,
                    'higher_rate': {
                        'rate': 40,
                        'range_start': 32001,
                        'range_end': 150000
                    },
                    'top_rate': None
                }},
                gross_salary=30000
            )
        msg = ("Personal Allowance data is missing, run command with -h to "
               "see available options.")
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_valid_json_full_data(self):
        year = "2018"
        year_data = IncomeTaxYearData(
            year=year,
            tax_data=DEFAULT_DATA,
            gross_salary=30000
        )
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
            IncomeTaxYearData(
                year=2016,
                tax_data={'foo': 'bar'},
                gross_salary=30000
            )

        msg = ('Data for year 2016 is not available, please run command with '
               '-h to see available options or try a different year. Data is '
               'available for the following years: foo')
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_year_is_null(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData(year=None, tax_data={}, gross_salary=32000)
        msg = "year can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_year_tax_data_is_null(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData(year=2016, tax_data=None, gross_salary=30000)
        msg = "year_tax_data can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_gross_salary_is_null(self):
        with self.assertRaises(ValueError) as cm:
            IncomeTaxYearData(year=2016, tax_data={}, gross_salary=None)
        msg = "gross_salary can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    # Not implemented method test stubs

    def test_add_not_implemented(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        with self.assertRaises(NotImplementedError):
            year_data.add()

    def test_edit_not_implemented(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        with self.assertRaises(NotImplementedError):
            year_data.edit()

    def test_delete_not_implemented(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        with self.assertRaises(NotImplementedError):
            year_data.delete()

    def test_save_not_implemented(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        with self.assertRaises(NotImplementedError):
            year_data.save()

    # Label functions tests

    def test_get_gross_salary_label(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_gross_salary_label()
        self.assertEqual(label, 'Gross Salary: £30,000.00\n')

    def test_get_personal_allowance_label(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_personal_allowance_label()
        self.assertEqual(year_data.personal_allowance, 11000)
        self.assertEqual(label, 'Personal Allowance: £11,000.00\n')

    def test_get_taxable_income_label(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_taxable_income_label()
        self.assertEqual(label, 'Taxable Income: £19,000.00\n')

    def test_get_band_label_no_rate(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_band_label('starter_rate')
        self.assertEqual(label, None)

    def test_get_band_label(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_band_label('basic_rate')
        self.assertEqual(label, "Basic Rate: £19,000.00 @ 20% = £3,800.00\n")

    def test_get_band_label_over_highest(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_band_label('higher_rate')
        self.assertEqual(label, None)

    def test_get_tax_due_label(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=30000
        )
        label = year_data.get_tax_due_label()
        self.assertEqual(label, "Total Tax Due: £3,800.00\n")

    def test_get_breakdown_short(self):
        year_data = IncomeTaxYearData(
            year=2016, tax_data=DEFAULT_DATA, gross_salary=25000
        )
        label = year_data.get_breakdown()
        self.assertEqual(
            label,
            "Gross Salary: £25,000.00\n\n"
            "Personal Allowance: £11,000.00\n\n"
            "Taxable Income: £14,000.00\n\n"
            "Basic Rate: £14,000.00 @ 20% = £2,800.00\n\n"
            "Total Tax Due: £2,800.00\n"
        )

    # Other tests
    def test_reset_tax_data(self):
        IncomeTaxYearData._reset_tax_data()
        with open(TAX_DATA_FILE_NAME) as json_file:
            tax_data = json.load(json_file)
        self.assertEqual(tax_data, json.loads(json.dumps(DEFAULT_DATA)))


class TestTaxBand(unittest.TestCase):
    def setUp(self):
        self.short_year_data = {
            'personal_allowance': 11000,
            'starter_rate': None,
            'basic_rate': {
                'rate': 20,
                'range_start': 0,
                'range_end': 32000
            },
            'intermediate_rate': None,
            'higher_rate': {
                'rate': 40,
                'range_start': 32001,
                'range_end': 150000
            },
            'top_rate': None
        }
        self.full_year_data = {
            'personal_allowance': 11850,
            'starter_rate': {
                'rate': 19,
                'range_start': 0,
                'range_end': 2000
            },
            'basic_rate': {
                'rate': 20,
                'range_start': 2001,
                'range_end': 12150
            },
            'intermediate_rate': {
                'rate': 21,
                'range_start': 12151,
                'range_end': 31580
            },
            'higher_rate': {
                'rate': 40,
                'range_start': 31581,
                'range_end': 150000
            },
            'top_rate': {
                'rate': 46,
                'range_start': 150000,
                'range_end': None
            }
        }

    def test_init_year_tax_data_is_null(self):
        with self.assertRaises(ValueError) as cm:
            TaxBand(
                year_tax_data=None, gross_salary=30000, band='starter_rate'
            )
        msg = "year_tax_data can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_gross_salary_is_null(self):
        with self.assertRaises(ValueError) as cm:
            TaxBand(
                year_tax_data={}, gross_salary=None, band='starter_rate'
            )
        msg = "gross_salary can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    def test_init_band_is_null(self):
        with self.assertRaises(ValueError) as cm:
            TaxBand(
                year_tax_data={}, gross_salary=30000, band=None
            )
        msg = "band can't be null"
        self.assertEqual(cm.exception.args[0], msg)

    def test_short_year_data_tax_calculation(self):
        band = TaxBand(
            year_tax_data=self.short_year_data,
            gross_salary=30000,
            band='basic_rate'
        )
        self.assertEqual(band.range_amount, 19000)
        self.assertEqual(band.band_deduction, 3800.0)

    def test_full_year_data_tax_calculation(self):
        band = TaxBand(
            year_tax_data=self.full_year_data,
            gross_salary=30000,
            band='basic_rate'
        )
        self.assertEqual(band.range_amount, 10149)
        self.assertEqual(band.band_deduction, 2029.8)

    def test_short_year_data_tax_calculation_bad_band(self):
        with self.assertRaises(ValueError) as cm:
            TaxBand(
                year_tax_data=self.short_year_data,
                gross_salary=40000,
                band='starter_rate'
            )
        msg = "This year does have the starter_rate band"
        self.assertEqual(cm.exception.args[0], msg)


if __name__ == '__main__':
    unittest.main()
