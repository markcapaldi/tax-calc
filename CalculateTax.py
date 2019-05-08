#!/usr/bin/python3

import argparse
import json
import locale
import logging

from defaults import DEFAULT_DATA, TAX_DATA_FILE_NAME

locale.setlocale(locale.LC_ALL, '')

help_text = '''Calculate the amount of Income tax due in a given tax year
for a given salary and provide a breakdown of the tax rates.'''

# Initiate the argument parser
parser = argparse.ArgumentParser(description=help_text)
parser.add_argument(
    "-v", "--verbose", help="increase output verbosity", action="store_true"
)
parser.add_argument(
    "-r", "--reset", help="reset tax data to defaults", action="store_true"
)
parser.add_argument(
    "-a", "--add-year", help="add tax data for a year", action="store_true"
)

parser.add_argument("tax_year", help="tax year for which to calculate tax",
                    type=int, nargs='?')
parser.add_argument("gross_income", help="gross income for the year",
                    type=int, nargs='?')

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def _reset_data():
    """populate JSON file with default data"""
    logging.debug('Reseting the Income Tax Data from defaults.')
    with open(TAX_DATA_FILE_NAME, 'w') as outfile:
        json.dump(DEFAULT_DATA, outfile)


class IncomeTaxData:

    PERSONAL_ALLOWANCE = 'personal_allowance'

    STARTER_RATE = 'starter_rate'
    BASIC_RATE = 'basic_rate'
    INTERMEDIATE_RATE = 'intermediate_rate'
    HIGHER_RATE = 'higher_rate'
    TOP_RATE = 'top_rate'

    GROSS_SALARY_LABEL = 'Gross Salary: {gross_salary}\n'
    TAXABLE_INCOME_LABEL = 'Taxable Income: {taxable_income}\n'
    PERSONAL_ALLOWANCE_LABEL = 'Personal Allowance: {personal_allowance}\n'

    RATE_LABELS = {
        STARTER_RATE:
            'Starter Rate: {amount} @ {rate}%\n',
        BASIC_RATE:
            'Basic Rate: {amount} @ {rate}%\n',
        INTERMEDIATE_RATE:
            'Intermediate Rate: {amount} @ {rate}%\n',
        HIGHER_RATE:
            'Higher Rate: {amount} @ {rate}%\n',
        TOP_RATE:
            'Top Rate: {amount} @ {rate}%\n',
    }

    def __init__(self, year, gross_salary=None):
        with open(TAX_DATA_FILE_NAME) as json_file:
            data = json.load(json_file)
            year_data = data[str(year)]

        def _get_rate_obj(rate_dict, rate):
            if rate_dict is not None:
                return Taxrate(rate_dict, rate)
            else:
                return None

        self.personal_allowance = year_data['personal_allowance']
        self.gross_salary = gross_salary

        if self.gross_salary:
            self.taxable_income = self.gross_salary - self.personal_allowance
        else:
            self.taxable_income = None

        self.starter_rate = _get_rate_obj(
            year_data[self.STARTER_RATE], self.STARTER_RATE
        )
        self.basic_rate = _get_rate_obj(
            year_data[self.BASIC_RATE], self.BASIC_RATE
        )
        self.intermediate_rate = _get_rate_obj(
            year_data[self.INTERMEDIATE_RATE], self.INTERMEDIATE_RATE
        )
        self.higher_rate = _get_rate_obj(
            year_data[self.HIGHER_RATE], self.HIGHER_RATE
        )
        self.top_rate = _get_rate_obj(
            year_data[self.TOP_RATE], self.TOP_RATE
        )

    def get_gross_salary_label(self):
        logging.debug('Getting Formated Gross Salary')
        return self.GROSS_SALARY_LABEL.format(
            gross_salary=locale.currency(self.gross_salary, grouping=True)
        )

    def get_personal_allowance_label(self):
        logging.debug('Getting Formated Personal Allowance')
        return self.PERSONAL_ALLOWANCE_LABEL.format(
            personal_allowance=locale.currency(
                self.personal_allowance, grouping=True
            )
        )

    def get_taxable_income_label(self):
        logging.debug('Getting Formated Taxable Income')
        return self.TAXABLE_INCOME_LABEL.format(
            taxable_income=locale.currency(self.taxable_income, grouping=True)
        )

    def get_rate_label(self, rate):
        logging.debug('Getting Formated %s', rate)
        tax_rate = getattr(self, rate)
        if tax_rate:
            return self.RATE_LABELS.get(rate).format(
                amount=locale.currency(
                    tax_rate.range_end - tax_rate.range_start,
                    grouping=True
                ),
                rate=tax_rate.rate
            )
        else:
            return None

    def get_breakdown(self):
        logging.debug('Getting Formated Tax Breakdown')
        message = ''
        if self.gross_salary:
            message += self.get_gross_salary_label()

        message += self.get_personal_allowance_label()

        if self.gross_salary:
            message += self.get_taxable_income_label()

        for rate in self.RATE_LABELS:
            rate_label = self.get_rate_label(rate)
            if rate_label:
                message += rate_label
        return message


class Taxrate:
    def __init__(self, rate_dict, name):
        self.name = name
        self.rate = rate_dict['rate']
        self.range_start = rate_dict['range_start']
        self.range_end = rate_dict['range_end']

    def __dict__(self):
        return {
            'rate': self.rate,
            'range_start': self.range_start,
            'range_end': self.range_end
        }


def main():
    logging.debug('Initializing Income Tax Calculator')
    try:
        logging.debug('Trying to load Tax Data from JSON.')
        with open(TAX_DATA_FILE_NAME) as json_file:
            json.load(json_file)
        logging.debug('Tax Data Loaded.')
    except json.decoder.JSONDecodeError:
        logging.debug('Income Tax Data is missing or is corrupt.')
        _reset_data()

    # Reset the Income Tax Data to Default
    if args.reset:
        _reset_data()
        logging.info('Income Tax Data has been reset.')
        return

    # Handle the case where only the year is provided
    if args.tax_year and not args.gross_income:
        data = IncomeTaxData(args.tax_year)
        logging.debug('Printing Tax Breakdown')
        print(
            "No Income Data Provided\n\n",
            "Showing tax rate data for tax year: {year_from}-{year_to}\n"
            "{breakdown}".format(
                year_from=args.tax_year,
                year_to=args.tax_year + 1,
                breakdown=data.get_breakdown()
            )
        )
        return


if __name__ == '__main__':
    main()
