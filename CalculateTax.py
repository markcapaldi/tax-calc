#!/usr/bin/python3

import argparse
import datetime
import json
import locale
import logging

from defaults import DEFAULT_DATA, TAX_DATA_FILE_NAME

locale.setlocale(locale.LC_ALL, '')


def _validate_year(value):
    """
    Validating user input for year to be a valid year
    """
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "%s is an invalid year value" % value
        )

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
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "%s is an invalid year value" % value
        )

    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            "%s is an invalid salary value" % value
        )
    return ivalue


class IncomeTaxYearData:
    """
    Object containing tax data and calculated variables based on gross salary,
    for a year

    init params:
        tax_data:     all available tax data
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

    def __init__(self, year=None, tax_data=None, gross_salary=None):
        if year is None:
            raise ValueError("year can't be null")

        if tax_data is None:
            raise ValueError("year_tax_data can't be null")

        if gross_salary is None:
            raise ValueError("gross_salary can't be null")

        if isinstance(year, int):
            year = str(year)

        if isinstance(tax_data, str):
            tax_data = json.loads(tax_data)

        try:
            year_tax_data = tax_data[year]
        except KeyError:
            raise ValueError(
                "Data for year %s is not available, please run command with "
                "-h to see available options or try a different year. Data is "
                "available for the following years: %s" %
                (year, ', '.join([_year for _year in tax_data]))
            )

        try:
            self.personal_allowance = year_tax_data['personal_allowance']
        except KeyError:
            msg = ('Personal Allowance data is missing, '
                   'run command with -h to see available options.')
            raise ValueError(msg)

        self.tax_data = tax_data
        self.year = year
        self.gross_salary = gross_salary
        self.taxable_income = self.gross_salary - self.personal_allowance

        for band in self.BANDS:
            if year_tax_data.get(band) and year_tax_data[band] is not None:
                setattr(
                    self, band, TaxBand(
                        year_tax_data=year_tax_data,
                        gross_salary=gross_salary,
                        band=band
                    )
                )
            else:
                setattr(self, band, None)

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
            return self.BANDS.get(rate).format(
                amount=locale.currency(
                    tax_band_obj.range_amount, grouping=True
                ),
                rate=str(tax_band_obj.rate)
            ) + ' = ' + locale.currency(
                tax_band_obj.band_deduction,
                grouping=True
            ) + '\n'

        return None

    def get_tax_due_label(self):
        total_tax = 0
        for band in self.BANDS:
            if getattr(self, band):
                total_tax += getattr(getattr(self, band), 'band_deduction')

        return (
            'Total Tax Due: ' +
            locale.currency(total_tax, grouping=True) + '\n'
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
            message += '\n' + self.get_tax_due_label()

        return message


class TaxBand:
    """
    Tax Band object containing information for a particular tax band
    """
    def __init__(self, year_tax_data=None, gross_salary=None, band=None):
        logging.debug('Initializing TaxBand %s', band)

        if gross_salary is None:
            raise ValueError("gross_salary can't be null")

        if year_tax_data is None:
            raise ValueError("year_tax_data can't be null")

        if band is None:
            raise ValueError("band can't be null")

        self.name = band
        try:
            self.rate = year_tax_data[band]['rate']
            self.range_start = year_tax_data[band]['range_start']
            self.range_end = year_tax_data[band]['range_end']
        except TypeError:
            raise ValueError("This year does have the %s band" % band)

        taxable_income = (
            gross_salary - year_tax_data['personal_allowance']
        )
        band_deductions = {}
        # We iterate through all the bands to calculate the deduction amount
        # for this band
        for band in IncomeTaxYearData.BANDS:
            if year_tax_data.get(band) and year_tax_data[band] is not None:
                # Save parameters of a band
                band_range_start = year_tax_data[band]['range_start']
                band_range_end = year_tax_data[band]['range_end']
                band_rate = year_tax_data[band]['rate']

                # Check that this is not an "infinite" band with no upper limit
                if band_range_end:
                    band_range_amount = band_range_end - band_range_start
                    # We still have money to be taxed above this band
                    if taxable_income > band_range_amount:
                        band_deductions[band] = {
                            'salary_part': band_range_amount,
                            'tax_deduction': (
                                (band_rate * band_range_amount) / 100.0
                            )
                        }
                        taxable_income -= band_range_amount
                    # There isn't any more money to be taxed in higher bands
                    else:
                        band_deductions[band] = {
                            'salary_part': taxable_income,
                            'tax_deduction': (
                                (band_rate * taxable_income) / 100.0
                            )
                        }
                        taxable_income = 0
                # Infinite band like "Over 150,000"
                else:
                    band_deductions[band] = {
                        'salary_part': taxable_income,
                        'tax_deduction': (
                            (band_rate * taxable_income) / 100.0
                        )
                    }
                    taxable_income = 0

        self.range_amount = band_deductions[self.name]['salary_part']
        self.band_deduction = band_deductions[self.name]['tax_deduction']

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

    # parser.add_argument(
    #     "-a", "--add-year",
    #     help="add tax data for a year", action="store_true"
    # )

    # parser.add_argument(
    #     "-e", "--edit-year",
    #     help="edit tax data for a year", action="store_true"
    # )

    # parser.add_argument(
    #     "-d", "--delete-year",
    #     help="delete tax data for a year", action="store_true"
    # )

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
            json_file.close()
        logging.debug('Tax Data Loaded.')
    except json.decoder.JSONDecodeError:
        logging.error('Tax data is missing or corrupt, '
                      'please try reseting tax data using -r parameter.')
        return

    try:
        tax_data = IncomeTaxYearData(
            args.tax_year, tax_data, args.gross_income
        )
    except KeyError:
        logging.error("Tax Data for year %s is not available, "
                      "you can add it using -a option." % args.tax_year)
        return

    # # Add Tax Data For a year
    # if args.add_year:
    #     logging.info('Adding tax data to the data store.')
    #     tax_data.add()
    #     return

    logging.debug('Printing Tax Breakdown with salary breakdown')
    print(
        "Tax Year: {year_from}-{year_to}\n\n"
        "{breakdown}".format(
            year_from=args.tax_year,
            year_to=args.tax_year + 1,
            breakdown=tax_data.get_breakdown()
        )
    )
    return


if __name__ == '__main__':
    main()
