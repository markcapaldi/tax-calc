#!/usr/bin/python3

import argparse
import datetime
import json
import locale
import logging

from functools import reduce

from defaults import DEFAULT_DATA, TAX_DATA_FILE_NAME

locale.setlocale(locale.LC_ALL, '')


def _validate_year(value):
    """
    Validating user input for year to be a valid year
    """
    ivalue = int(value)
    if (
        ivalue <= 0 or
        ivalue >= datetime.datetime.now().year + 1
    ):
        raise argparse.ArgumentTypeError(
            "%s is an invalid year value" % value
        )
    return ivalue


def _validate_salary(value):
    """
    Validating user input for salary to be a positive integer
    """
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            "%s is an invalid salary value" % value
        )
    return ivalue


class IncomeTaxYearData:
    """
    Object containing tax data and calculated variables based on gross salary,

    init params:
        year_tax_data: tax data for a particular year in a dict form
        gross_salary: salary used to calculate variable portions of tax
                      deductions like personal allowance and tax deductions
                      per band.
    """
    PERSONAL_ALLOWANCE = 'personal_allowance'

    STARTER_RATE = 'starter_rate'
    BASIC_RATE = 'basic_rate'
    INTERMEDIATE_RATE = 'intermediate_rate'
    HIGHER_RATE = 'higher_rate'
    TOP_RATE = 'top_rate'

    GROSS_SALARY_LABEL = 'Gross Salary: {gross_salary}'
    TAXABLE_INCOME_LABEL = 'Taxable Income: {taxable_income}'
    PERSONAL_ALLOWANCE_LABEL = 'Personal Allowance: {personal_allowance}'

    BANDS = {
        STARTER_RATE:
            'Starter Rate: {amount} @ {rate}%',
        BASIC_RATE:
            'Basic Rate: {amount} @ {rate}%',
        INTERMEDIATE_RATE:
            'Intermediate Rate: {amount} @ {rate}%',
        HIGHER_RATE:
            'Higher Rate: {amount} @ {rate}%',
        TOP_RATE:
            'Top Rate: {amount} @ {rate}%',
    }

    def __init__(self, year_tax_data, gross_salary):
        if year_tax_data is None:
            raise ValueError("year_tax_data can't be null")

        if gross_salary is None:
            raise ValueError("gross_salary can't be null")

        try:
            self.personal_allowance = year_tax_data['personal_allowance']
        except KeyError:
            msg = ('Personal Allowance data is missing or corrupt, '
                   'please try reseting tax data using -r parameter.')
            raise ValueError(msg)

        self.gross_salary = gross_salary
        self.taxable_income = self.gross_salary - self.personal_allowance

        for rate in self.BANDS:
            if year_tax_data.get(rate) and year_tax_data[rate] is not None:
                setattr(self, rate, TaxBand(year_tax_data, gross_salary, rate))
            else:
                setattr(self, rate, None)

    def add(self, *args, **kwargs):
        """Add Tax Data for a year"""
        return self.edit(self, *args, **kwargs)

    def edit(self, *args, **kwargs):
        """Edit Tax Data for a year"""
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        """Delete Tax Data for a year"""
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """Save the data from the object into the JSON file."""
        raise NotImplementedError

    def _reset_tax_data():
        """Populate JSON file with default data"""
        logging.debug('Reseting the Income Tax Data from defaults.')
        with open(TAX_DATA_FILE_NAME, 'w') as outfile:
            json.dump(DEFAULT_DATA, outfile)

    def get_gross_salary_label(self):
        logging.debug('Getting Formated Gross Salary')
        return self.GROSS_SALARY_LABEL.format(
            gross_salary=locale.currency(self.gross_salary, grouping=True)
        ) + '\n'

    def get_personal_allowance_label(self):
        logging.debug('Getting Formated Personal Allowance')
        return self.PERSONAL_ALLOWANCE_LABEL.format(
            personal_allowance=locale.currency(
                self.personal_allowance, grouping=True
            )
        ) + '\n'

    def get_taxable_income_label(self):
        logging.debug('Getting Formated Taxable Income')
        return self.TAXABLE_INCOME_LABEL.format(
            taxable_income=locale.currency(self.taxable_income, grouping=True)
        ) + '\n'

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
                ) + '\n'
        else:
            return None

    def get_tax_due_label(self):
        return (
            'Total Tax Due: ' +
            locale.currency(
                reduce(
                    lambda x, y: x + y,
                    [
                        getattr(getattr(self, rate), 'band_deduction')
                        for rate in self.BANDS
                    ]
                ),
                grouping=True
            ) + '\n'
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
    def __init__(self, year_tax_data, gross_salary, band):
        logging.debug('Initializing TaxBand %s', band)
        self.name = band
        self.rate = year_tax_data[band]['rate']
        self.range_start = year_tax_data[band]['range_start']
        self.range_end = year_tax_data[band]['range_end']
        self.range_amount = 0
        self.band_deduction = 0

    def __dict__(self):
        return {
            'rate': self.rate,
            'range_start': self.range_start,
            'range_end': self.range_end,
        }


def main():
    """
    Main function thread setting up the argument parsing and directing the flow
    of the application.
    """
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
        help="tax year for which to calculate tax", type=_validate_year
    )
    parser.add_argument(
        "gross_income",
        help="gross income for the year", type=_validate_salary
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
