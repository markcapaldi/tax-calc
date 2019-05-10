#!/usr/bin/python3

import argparse
import json
import locale
import logging

from functools import reduce

from defaults import DEFAULT_DATA, TAX_DATA_FILE_NAME


class IncomeTaxYearData:
    """
    Object containing tax data and calculations,

    init params:
        year_tax_data(required): tax data for a particular year in a dict form
        gross_salary: salary used to calculate variable portions
                                of tax deductions like personal allowance and
                                tax deductions per band.
    """
    PERSONAL_ALLOWANCE = 'personal_allowance'

    STARTER_RATE = 'starter_rate'
    BASIC_RATE = 'basic_rate'
    INTERMEDIATE_RATE = 'intermediate_rate'
    HIGHER_RATE = 'higher_rate'
    TOP_RATE = 'top_rate'

    GROSS_SALARY_LABEL = 'Gross Salary: {gross_salary}\n'
    TAXABLE_INCOME_LABEL = 'Taxable Income: {taxable_income}\n'
    PERSONAL_ALLOWANCE_LABEL = 'Personal Allowance: {personal_allowance}\n'

    BANDS = {
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

    def __init__(self, year_tax_data, gross_salary):
        def _get_rate_obj(band_dict, band):
            if band_dict is not None:
                return TaxBand(band_dict, band)
            else:
                return None
        try:
            self.personal_allowance = year_tax_data['personal_allowance']
        except KeyError:
            logging.error('Personal Allowance data is missing or corrupt, '
                          'please try reseting tax data using -r parameter.')
            return

        self.gross_salary = gross_salary
        self.taxable_income = self.gross_salary - self.personal_allowance


        salary_remainder = self.taxable_income
        for rate in self.BANDS:
            setattr(
                self, rate, _get_rate_obj(year_tax_data[rate], rate)
            )
            rate_attr = getattr(self, rate)
            if rate_attr:
                if rate_attr.range_end and salary_remainder > 0:
                    salary_remainder -= (
                        rate_attr.range_end - rate_attr.range_start
                    )

                    rate_attr.range_amount = salary_remainder
                    rate_attr.band_deduction = (
                        (rate_attr.rate * salary_remainder) / 100.0
                    )
            setattr(self, rate, rate_attr)

    def _reset_tax_data():
        """Populate JSON file with default data"""
        logging.debug('Reseting the Income Tax Data from defaults.')
        with open(TAX_DATA_FILE_NAME, 'w') as outfile:
            json.dump(DEFAULT_DATA, outfile)

    def _add_tax_year_data():
        """Add Tax Data to the JSON file"""
        raise NotImplementedError

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

    def get_band_label(self, rate):
        logging.debug('Getting Formated %s', rate)
        tax_band_obj = getattr(self, rate)
        if not tax_band_obj:
            return None

        if tax_band_obj.band_deduction:
            if tax_band_obj.range_amount:
                return self.BANDS.get(rate).format(
                    amount=locale.currency(
                        tax_band_obj.range_amount, grouping=True
                    ),
                    rate=(
                        str(tax_band_obj.rate) + ' = ' +
                        locale.currency(
                            tax_band_obj.band_deduction,
                            grouping=True
                        )
                    )
                )
        else:
            return None

    def get_tax_due_label(self):
        return (
            '\nTotal Tax Due: ' +
            locale.currency(
                reduce(
                    lambda x, y: x + y,
                    [
                        getattr(getattr(self, rate), 'band_deduction')
                        for rate in self.BANDS
                    ]
                ),
                grouping=True
            )
        )

    def get_breakdown(self):
        logging.debug('Getting Formated Tax Breakdown')
        message = ''
        if self.gross_salary:
            message += self.get_gross_salary_label() + '\n'

        message += self.get_personal_allowance_label() + '\n'

        if self.gross_salary:
            message += self.get_taxable_income_label() + '\n'

        for rate in self.BANDS:
            band_label = self.get_band_label(rate)
            if band_label:
                message += band_label

        if self.gross_salary:
            message += self.get_tax_due_label()

        return message


class TaxBand:
    """
    Tax Band object containing information for a particular tax band
    """
    def __init__(self, band_dict, band):
        logging.debug('Initializing TaxBand %s', band)
        self.name = band
        self.rate = band_dict['rate']
        self.range_start = band_dict['range_start']
        self.range_end = band_dict['range_end']
        self.range_amount = 0
        self.band_deduction = 0

    def __dict__(self):
        return {
            'rate': self.rate,
            'range_start': self.range_start,
            'range_end': self.range_end,
        }


def main():
    # Setting up environment

    locale.setlocale(locale.LC_ALL, '')

    help_text = '''Calculate the amount of Income tax due in a given tax year
    for a given salary and provide a breakdown of the tax bands.'''

    # Initiate the argument parser
    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument(
        "-v", "--verbose",
        help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-r", "--reset",
        help="reset tax data to defaults", action="store_true"
    )
    parser.add_argument(
        "-a", "--add-year",
        help="add tax data for a year", action="store_true"
    )

    parser.add_argument(
        "tax_year",
        help="tax year for which to calculate tax", type=int
    )
    parser.add_argument(
        "gross_income",
        help="gross income for the year", type=int
    )

    args = parser.parse_args()

    # Reset the Income Tax Data to Default
    if args.reset:
        IncomeTaxYearData._reset_tax_data()
        logging.info('Income Tax Data has been reset.')
        return

    # Add Tax Data For a year
    if args.add_year:
        logging.info('Adding tax data to the data store.')
        IncomeTaxYearData._add_tax_year_data()
        return

    # Setting logging verbosity level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug('Initializing Income Tax Calculator')
    try:
        logging.debug('Trying to load Tax Data from JSON.')
        with open(TAX_DATA_FILE_NAME) as json_file:
            tax_data = json.load(json_file)
        logging.debug('Tax Data Loaded.')
    except json.decoder.JSONDecodeError:
        logging.error('Tax data is missing or corrupt, '
                      'please try reseting tax data using -r parameter.')
        return

    try:
        data = IncomeTaxYearData(
            tax_data[str(args.tax_year)],
            args.gross_income
        )
    except KeyError:
        logging.error("Tax Data for year %s is not available, "
                      "you can add it using -a option." % args.tax_year)
        return

    logging.debug('Printing Tax Breakdown with salary breakdown')
    print(
        "Tax Year: {year_from}-{year_to}\n"
        "{breakdown}".format(
            year_from=args.tax_year,
            year_to=args.tax_year + 1,
            breakdown=data.get_breakdown()
        )
    )
    return


if __name__ == '__main__':
    main()
