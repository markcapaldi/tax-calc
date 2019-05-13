Application to Calculate the amount of Income tax due in a given tax year for a given salary
and provide a breakdown of the tax bands.

Requirements:

    python3

Installation:

    sudo apt install python3-pip

Usage:

    ./CalculateTax.py [-h] [-v] [-r] tax_year gross_income
    
positional arguments:

    tax_year       tax year for which to calculate tax
  
    gross_income   gross income for the year
  

optional arguments:

    -h, --help     show help message and exit
  
    -v, --verbose  increase output verbosity
  
    -r, --reset    reset tax data to defaults
