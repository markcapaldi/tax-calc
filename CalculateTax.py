#!/usr/bin/python3

import argparse
import logging


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


def main():
    logging.debug('Initializing Income Tax Calculator')


if __name__ == '__main__':
    main()
