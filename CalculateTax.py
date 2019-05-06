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

    PERSONAL_ALLOWANCE = 'personal_allowance'

    STARTER_RATE = 'starter_rate'
    BASIC_RATE = 'basic_rate'
    INTERMEDIATE_RATE = 'intermediate_rate'
    HIGHER_RATE = 'higher_rate'
    TOP_RATE = 'top_rate'

    PERSONAL_ALLOWANCE_LABEL = 'Personal Allowance'

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
            year_data = data[str(year)]

        def _get_band_obj(rate_dict, rate):
            if rate_dict is not None:
                return TaxBand(rate_dict, rate)
            else:
                return None

        self.personal_allowance = year_data['personal_allowance']

        self.starter_rate = _get_band_obj(
            year_data[self.STARTER_RATE], self.STARTER_RATE
        )
        self.basic_rate = _get_band_obj(
            year_data[self.BASIC_RATE], self.BASIC_RATE
        )
        self.intermediate_rate = _get_band_obj(
            year_data[self.INTERMEDIATE_RATE], self.INTERMEDIATE_RATE
        )
        self.higher_rate = _get_band_obj(
            year_data[self.HIGHER_RATE], self.HIGHER_RATE
        )
        self.top_rate = _get_band_obj(
            year_data[self.TOP_RATE], self.TOP_RATE
        )


class TaxBand:
    def __init__(self, band_dict, name):
        self.name = name
        self.rate = band_dict['rate']
        self.range_start = band_dict['range_start']
        self.range_end = band_dict['range_end']

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
    except json.decoder.JSONDecodeError:
        logging.error('Income Tax Data is missing or is corrupt.')
        _reset_data()


if __name__ == '__main__':
    main()
