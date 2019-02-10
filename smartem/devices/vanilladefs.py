from devicefuncs import *

# All sensor definitions, no conversion required.
SENSOR_DEFS = {
    'temperature':
        {
            'label': 'Temperatuur',
            'unit': 'Celsius',
            'input': 'temperature',
            'meta_id': 'TBD',
            # Is already in Celsius
            'converter': convert_none,
            'type': int,
            'min': -25,
            'max': 70
        },
    'pressure':
        {
            'label': 'Luchtdruk',
            'unit': 'HectoPascal',
            'input': 'pressure',
            'meta_id': 'TBD',
            # Is already in HectoPascal
            'converter': convert_none,
            'type': int,
            'min': 200,
            'max': 1100
        },
    'humidity':
        {
            'label': 'Luchtvochtigheid',
            'unit': 'Procent',
            'input': 'humidity',
            'meta_id': 'TBD',
            # Is already in percent
            'converter': convert_none,
            'type': int,
            'min': 20,
            'max': 100
        },
    'co':
        {
            'label': 'CO',
            'unit': 'ug/m3',
            'input': 'co',
            'meta_id': 'TBD',
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 10000
        },
    'no':
        {
            'label': 'NO',
            'unit': 'ug/m3',
            'input': 'no',
            'meta_id': 'TBD',
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 2000
        },
    'no2':
        {
            'label': 'NO2',
            'unit': 'ug/m3',
            'input': 'no2',
            'meta_id': 'TBD',
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 250
        },
    'o3':
        {
            'label': 'O3',
            'unit': 'ug/m3',
            'input': 'o3',
            'meta_id': 'TBD',
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 300
        },
    'pm10': {
        'label': 'PM 10',
        'unit': 'ug/m3',
        'input': 'pm10',
        'meta_id': 'TBD',
        'converter': convert_none,
        'type': int,
        'min': 0,
        'max': 999,
    },

    'pm2_5': {
        'label': 'PM 2.5',
        'unit': 'ug/m3',
        'input': 'pm2_5',
        'meta_id': 'TBD',
        'converter': convert_none,
        'type': int,
        'min': 0,
        'max': 999
    },

    'pm1': {
        'label': 'PM 1',
        'unit': 'ug/m3',
        'input': 'pm1',
        'meta_id': 'TBD',
        'converter': convert_none,
        'type': int,
        'min': 0,
        'max': 999
    }
}
