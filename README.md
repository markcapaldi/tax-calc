Application to Calculate the amount of Income tax due in a given tax year for a given salary
and provide a breakdown of the tax bands.

Requirements:

    python3

Installation:
It is highly recomended to wortk in a python virtual environment.

    sudo apt install python3-pip python-dev gcc
    sudo pip3 install virtualenv 
    virtualenv -p /usr/bin/python3 tax-venv
    source tax-venv/bin/activate
    pip install coverage

Usage:

    ./CalculateTax.py [-h] [-v] [-r] tax_year gross_income
    
positional arguments:

    tax_year       tax year for which to calculate tax
  
    gross_income   gross income for the year
  

optional arguments:

    -h, --help     show help message and exit
  
    -v, --verbose  increase output verbosity
  
    -r, --reset    reset tax data to defaults
    
    
To run tests call:
    
    coverage run tests.py
    
To update coverage report run:

    coverage html
    
To view the coverage report open index.html in /htmlcov folder.

