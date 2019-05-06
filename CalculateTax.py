#!/usr/bin/python3

import argparse
import logging
import json

from defaults import DEFAULT_DATA, TAX_DATA_FILE_NAME


help_text = '''Calculate the amount of Income tax due in a given tax year
for a given salary and provide a breakdown of the tax rates.'''

# Initiate the argument parser
parser = argparse.ArgumentParser(description=help_text)
parser.add_argument(
    "-v", "--verbose", help="increase output verbosity", action="store_true"
)
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)


def _reset_data():
    """populate JSON file with default data"""
    logging.debug('Reseting the Income Tax Data from defaults.')
    with open(TAX_DATA_FILE_NAME, 'w') as outfile:
        json.dump(DEFAULT_DATA, outfile)


class IncomeTaxData:

    STARTER_RATE = 'starter_rate'
    BASIC_RATE = 'basic_rate'
    INTERMEDIATE_RATE = 'intermediate_rate'
    HIGHER_RATE = 'higher_rate'
    TOP_RATE = 'top_rate'

    BANDS_LABELS = (
        (STARTER_RATE, 'Starter Rate'),
        (BASIC_RATE, 'Basic Rate'),
        (INTERMEDIATE_RATE, 'Intermediate Rate'),
        (HIGHER_RATE, 'Higher Rate'),
        (TOP_RATE, 'Top Rate'),
    )

    def __init__(self, year):
        with open(TAX_DATA_FILE_NAME) as json_file:
            data = json.load(json_file)

        try:
            year_data = data[year]
        except KeyError:
            logging.info(
                'Income Tax Data for year {year} is not available.', year
            )
            return None

        self.personal_allowance = year_data['personal_allowance']

        self.starter_rate = year_data[self.STARTER_RATE]
        self.basic_rate = year_data[self.BASIC_RATE]
        self.intermediate_rate = year_data[self.INTERMEDIATE_RATE]
        self.higher_rate = year_data[self.HIGHER_RATE]
        self.top_rate = year_data[self.TOP_RATE]


def main():
    logging.debug('Initializing Income Tax Calculator')


if __name__ == '__main__':
    main()
