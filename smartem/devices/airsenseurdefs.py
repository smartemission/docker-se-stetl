from devicefuncs import *
from airsenseurfuncs import *

# All sensor definitions, both base sensors (AirSensEUR) and derived (virtual) sensors
# Carbon_monoxide = c("co_a4","CO-B4", "CO_MF_200", "CO_MF_20", "COMF200", "CO3E300","co_mf_200"),
# Nitric_oxide = c("no_b4","NOB4_P1_op1","NOB4_P1", "NO_C_25", "NO/C-25","NO3E100"))
# Nitrogen_dioxide = c("no2_b43f","NO2-B43F", "NO2_C_20", "NO2/C-20", "NO23E50"),
# Ozone = c("o3_a431","O3_M-5","O3_M5", "O3-B4", "O33EF1","o3_m_5"),

# Names
# Geonovum1 ASE
# 'COMF200', 'NOB4_P1', 'NO2-B43F' 'O3_M5'
# JustObjects1 ASE
# 'COMF200', 'NOB4_P1', 'NO2-B43F' 'O3_M5'

# ASENL Deploy - 2018
# 'COA4', 'NOB4', 'NO2B43F' 'OX_A341'

# References:
# [1] "Evaluation of low-cost sensors for air pollution monitoring"
# by Spinelle, L., Gerboles, M., Kotsev, A. and Signorini, M. (2017)
# Technical report by the Joint Research Centre (JRC), the European
# Commission's science and knowledge service.
# JRC106095 EUR 28601 EN
#
# [2] https://www.samenmetenaanluchtkwaliteit.nl/sites/default/files/2017-12/Jan%20Vonk_AirSensEUR.pptx.pdf
# Jan Vonk - RIVM

# 17.01.2019 Michel Gerboles:
#   name.sensor Sens.raw.unit  gas.sensor       RefAD        Ref         board.zero.set   GAIN   Rload
# 1     COA4            nA     Carbon_monoxide  0.5006105    1.500611    1.1003053        7001     50
# 3     NOB4            nA     Nitric_oxide     0.5006105    1.200244    0.8315018        7001     50
# 2     NO2B43F         nA     Nitrogen_dioxide 0.5006105    1.700855    2.1507937        7001     50
# 4     OX_A431         nA     Ozone            0.5006105    1.700855    2.1507937        7001     50

# For now only support for AlphaSense (NO, NO2) and Membrapor (CO, O3) sensors.
SENSOR_DEFS = {
    'COA4':
        {
            'label': 'CORaw',
            'vendor': 'AlphaSense',
            'meta': 'http://www.alphasense.com/WEB1213/wp-content/uploads/2017/01/COA4.pdf',
            'unit': 'digital',
            'meta_id': 'COA4',
            'params': {
                'v_ref': 1.500611,
                'v_ref_ad': 0.5006105,
                'gain': 7001.0,
                'r_load': 50.0,
            },
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 65535
        },
    'NOB4':
        {
            'label': 'NORaw',
            'vendor': 'AlphaSense',
            'meta': 'http://www.alphasense.com/WEB1213/wp-content/uploads/2015/03/NO-B4.pdf',
            'unit': 'digital',
            'meta_id': 'NOB4',
            'params': {
                'v_ref': 1.200244,
                'v_ref_ad': 0.5006105,
                'gain': 7001.0,
                'r_load': 50.0,
            },
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 65535
        },
    'NO2B43F':
        {
            'label': 'NO2Raw',
            'vendor': 'AlphaSense',
            'meta': 'http://www.alphasense.com/WEB1213/wp-content/uploads/2017/07/NO2B43F.pdf',
            'unit': 'digital',
            'meta_id': 'NO2B43F',
            'params': {
                'v_ref': 1.700855,
                'v_ref_ad': 0.5006105,
                'gain': 7001.0,
                'r_load': 50.0,
            },
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 65535
        },
    'OX_A431':
        {
            'label': 'OX_A431',
            'vendor': 'AlphaSense',
            'meta': 'http://www.alphasense.com/WEB1213/wp-content/uploads/2017/03/OX-A431.pdf',
            'unit': 'digital',
            'meta_id': 'OX_A431',
            'params': {
                'v_ref': 1.700855,
                'v_ref_ad': 0.5006105,
                'gain': 7001.0,
                'r_load': 50.0,
            },
            'converter': convert_none,
            'type': int,
            'min': 0,
            'max': 65535
        },

    'Tempe':
        {
            'label': 'Temperatuur',
            'unit': 'Celsius',
            'min': -25,
            'max': 60
        },
    'Press':
        {
            'label': 'Luchtdruk',
            'unit': 'HectoPascal',
            'min': 200,
            'max': 1100

        },
    'Humid':
        {
            'label': 'Relative Humidity',
            'unit': '%RH',
            'min': 20,
            'max': 100
        },
    'temperature':
        {
            'label': 'Temperatuur',
            'unit': 'Celsius',
            'input': 'Tempe',
            'meta_id': 'ase-Tempe',
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
            'input': 'Press',
            'meta_id': 'ase-Press',
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
            'input': 'Humid',
            'meta_id': 'ase-Humid',
            # Is already in percent
            'converter': convert_none,
            'type': int,
            'min': 20,
            'max': 100
        },
    'coraw':
        {
            'label': 'CORaw',
            'unit': 'nanoAmpere',
            'input': ['COA4'],
            'min': 0,
            'max': 10000,
            'converter': rec_digital2nano_ampere,
        },
    'noraw':
        {
            'label': 'NORaw',
            'unit': 'nanoAmpere',
            'input': ['NOB4'],
            'min': 0,
            'max': 10000,
            'converter': rec_digital2nano_ampere,
        },
    'no2raw':
        {
            'label': 'NO2Raw',
            'unit': 'nanoAmpere',
            'input': ['NO2B43F'],
            'min': 0,
            'max': 10000,
            'converter': rec_digital2nano_ampere,
        },
    'o3raw':
        {
            'label': 'O3Raw',
            'unit': 'nanoAmpere',
            'input': ['OX_A431'],
            'min': 0,
            'max': 10000,
            'converter': rec_digital2nano_ampere,
        },
    'co':
        {
            'label': 'CO',
            'unit': 'ug/m3',
            'input': ['coraw'],
            'meta_id': 'COA4',
            'converter': rec_nano_ampere_co_to_ugm3,
            'type': int,
            'min': 0,
            'max': 10000
        },
    'no':
        {
            'label': 'NO',
            'unit': 'ug/m3',
            'input': ['noraw'],
            'meta_id': 'NOB4',
            'converter': rec_nano_ampere_no_to_ugm3,
            'type': int,
            'min': 0,
            'max': 200
        },
    'no2':
        {
            'label': 'NO2',
            'unit': 'ug/m3',
            'input': ['no2raw'],
            'meta_id': 'NO2B43F',
            'converter': rec_nano_ampere_no2_to_ugm3,
            'type': int,
            'min': 0,
            'max': 200
        },
    'o3':
        {
            'label': 'O3',
            'unit': 'ug/m3',
            'input': ['o3raw'],
            'meta_id': 'OX_A431',
            'converter': rec_nano_ampere_o3_to_ugm3,
            'type': int,
            'min': 0,
            'max': 1000
        }

}

# OBSOLETE
# 'CO3E300':
#     {
#         'label': 'CORaw',
#         'vendor': 'CityTech',
#         'meta': 'https://www.thebigredguide.com/docs/fullspec/co3e300.pdf',
#         'unit': 'unknown',
#         'meta_id': 'CO3E300',
#         'converter': convert_none,
#         'type': int,
#         'min': 10,
#         'max': 150000
#     },
# 'COMF200':
#     {
#         'label': 'CORaw',
#         'vendor': 'Membrapor',
#         'meta': 'http://www.membrapor.ch/sheet/CO-MF-200.pdf',
#         'unit': 'unknown',
#         'meta_id': 'COMF200',
#         'params': {
#             'v_ref': 2,
#             'v_ref_ad': 1
#         },
#         'converter': convert_none,
#         'type': int,
#         'min': 0,
#         'max': 65535
#     },

# 'O3_M5':
#     {
#         'label': 'O3Raw',
#         'vendor': 'Membrapor',
#         'meta': 'http://www.diltronic.com/wordpress/wp-content/uploads/O3-M-5.pdf',
#         'unit': 'unknown',
#         'meta_id': 'O3_M5',
#         'params': {
#             'v_ref': 1.7,
#             'v_ref_ad': 0.5
#         },
#         'converter': convert_none,
#         'type': int,
#         'min': 0,
#         'max': 65535
#     },
# 'NOB4_P1':
#     {
#         'label': 'NORaw',
#         'vendor': 'AlphaSense',
#         'meta': 'http://www.alphasense.com/WEB1213/wp-content/uploads/2015/03/NOB4_P1.pdf',
#         'unit': 'unknown',
#         'meta_id': 'NOB4_P1',
#         'params': {
#             'v_ref': 1.7,
#             'v_ref_ad': 1
#         },
#         'converter': convert_none,
#         'type': int,
#         'min': 0,
#         'max': 65535
#     },
