TAX_DATA_FILE_NAME = "tax_data.json"

DEFAULT_DATA = {
    2015: {
        'personal_allowance': 10600,
        'starter_rate': None,
        'basic_rate': {
            'rate': 20,
            'range_start': 0,
            'range_end': 31785
        },
        'intermediate_rate': None,
        'higher_rate': {
            'rate': 40,
            'range_start': 31786,
            'range_end': 150000
        },
        'top_rate': None
    },
    2016: {
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
    },
    2017: {
        'personal_allowance': 11500,
        'starter_rate': None,
        'basic_rate': {
            'rate': 20,
            'range_start': 0,
            'range_end': 31500
        },
        'intermediate_rate': None,
        'higher_rate': {
            'rate': 40,
            'range_start': 31501,
            'range_end': 150000
        },
        'top_rate': None
    },
    2018: {
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
}
