#
# Conversion functions for raw values from ASE-based sensors
#
#
# References:
# [1] "Evaluation of low-cost sensors for air pollution monitoring"
# by Spinelle, L., Gerboles, M., Kotsev, A. and Signorini, M. (2017)
# Technical report by the Joint Research Centre (JRC), the European
# Commission's science and knowledge service.
# JRC106095 EUR 28601 EN
#
# [2] https://www.samenmetenaanluchtkwaliteit.nl/sites/default/files/2017-12/Jan%20Vonk_AirSensEUR.pptx.pdf
# Jan Vonk - RIVM
#

from airsenseurparms import get_parms

TWO_POW_16 = 65536.0
TEN_POW_9 = float(pow(10, 9))


# Equation 1: [1] page 3
# STEP 1 Digital to Voltage (V)
# V = (Ref - RefAD) + (Digital+1) /2^16 x 2 x RefAD
# STEP 2 Voltage (V) to Ampere (I) as Ri
# I = 10^9 V/(Gain x Rload)
def digital2nano_ampere(value, device, sensor_name):
    input_def = device.get_sensor_def(sensor_name)
    params = input_def['params']

    # STEP 1 Digital to Voltage (V)
    # V = (Ref - RefAD) + (Digital+1) /2^16 x 2 x RefAD
    Ref = params['v_ref']
    RefAD = params['v_ref_ad']
    Digital = value
    V = (Ref - RefAD) + (Digital + 1) / TWO_POW_16 * 2.0 * RefAD
    # V = 0.844020396835

    # STEP 2 Voltage (V) to Ampere (I) as Ri
    # I = 10^9 V/(Gain x Rload)
    Gain = params['gain']
    RLoad = params['r_load']
    I = TEN_POW_9 * V / (Gain * RLoad)

    return I


# Equation 1: [1] page 3
# STEP 1 Digital to Voltage (V)
# V = (Ref - RefAD) + (Digital+1) /2^16 x 2 x RefAD
# STEP 2 Voltage (V) to Ampere (I) as Ri
# I = 10^9 V/(Gain x Rload)
def rec_digital2nano_ampere(value, record_in=None, sensor_def=None, device=None):
    """
    Convert (evaluated) bits value to millivolt according to Vref and RefAD ASE formulas.

    :param int value: input value raw 2 byte number 0..65535
    :param dict json_obj: complete record data object
    :param dict sensor_def:
    :param object: the device object:
    :return:
    """
    # e.g. 'NO2-B43F'
    sensor_name = record_in['name']
    input_names = sensor_def['input']
    if sensor_name not in input_names:
        return None

    return digital2nano_ampere(value, device, sensor_name)

#
# Gas nA to mg/m3 funcs
#


def nano_ampere_co_to_ugm3(device_id, Ri, RH):
    # STEP 3 Per-sensor Linear equation CO
    # Ri=a0+a1*CO+a2*RH
    # a0-a3 for ASE_NL01 CO (page 28)
    parms = get_parms(device_id, 'co')
    if not parms:
        return None

    co = ((Ri - parms['a0'] - parms['a2'] * RH) / parms['a1'])
    return co


def rec_nano_ampere_co_to_ugm3(nA, record_in=None, sensor_def=None, device=None):
    """
    Convert (evaluated) nanoAmpere to ug/m3

    :param int value: input value nano Ampere (nA)
    :param dict json_obj: complete record data object
    :param dict sensor_def:
    :param object: the device object:
    :return: co2 in ug/m3
    """
    device_id = record_in['device_id']
    RH = None
    try:
        RH = device.get_last_value(device_id, 'humidity', None)['value']
    except:
        pass

    if RH is None:
        return None

    return nano_ampere_co_to_ugm3(device_id, nA, RH)


def nano_ampere_no_to_ugm3(device_id, Ri, T):
    # STEP 3 Per-sensor Linear equation NO2
    # Ri=a0+a1*NO+a2*T +a3*T*T
    # a0-a3 for ASE_NL01 NOB4 (page 28)
    parms = get_parms(device_id, 'no')
    if not parms:
        return None
    no = ((Ri - parms['a0'] - parms['a2'] * T - parms['a3'] * T * T) / parms['a1'])
    return no


def rec_nano_ampere_no_to_ugm3(nA, record_in=None, sensor_def=None, device=None):
    """
    Convert (evaluated) nanoAmpere to ug/m3

    :param int value: input value nano Ampere (nA)
    :param dict json_obj: complete record data object
    :param dict sensor_def:
    :param object: the device object:
    :return: no in ug/m3
    """
    device_id = record_in['device_id']
    T = None
    try:
        T = device.get_last_value(device_id, 'temperature', None)['value']
    except:
        pass

    if T is None:
        return None

    return nano_ampere_no_to_ugm3(device_id, nA, T)

def nano_ampere_no2_to_ugm3(device_id, nA, T):
    # STEP 3 Per-sensor Linear equation NO2
    # Ri=a0+a1*NO2+a2*T
    # a0-a2 for ASE_NL01 NO2B43F (page 28)
    parms = get_parms(device_id, 'no2')
    if not parms:
        return None

    no2 = ((nA - parms['a0'] - parms['a2'] * T) / parms['a1'])
    if no2 < 3:
        return None
    return no2


def rec_nano_ampere_no2_to_ugm3(nA, record_in=None, sensor_def=None, device=None):
    """
    Convert (evaluated) nanoAmpere to ug/m3

    :param int value: input value nano Ampere (nA)
    :param dict json_obj: complete record data object
    :param dict sensor_def:
    :param object: the device object:
    :return: no2 in ug/m3
    """
    device_id = record_in['device_id']
    T = None
    try:
        T = device.get_last_value(device_id, 'temperature', None)['value']
    except:
        pass

    if T is None:
        return None

    return nano_ampere_no2_to_ugm3(device_id, nA, T)

def nano_ampere_o3_to_ugm3(device_id, Ri, T, no2):
    # STEP 3 Per-sensor Linear equation O3
    # Ri=a0+a1*O3+a2*NO2(sensor)+a3* T
    # a0-a3 for ASE_NL01 O3
    parms = get_parms(device_id, 'o3')
    if not parms:
        return None
    o3 = ((Ri - parms['a0'] - parms['a2'] * no2 - parms['a3'] * T) / parms['a1'])
    return o3


def rec_nano_ampere_o3_to_ugm3(nA, record_in=None, sensor_def=None, device=None):
    """
    Convert (evaluated) nanoAmpere to ug/m3

    :param int value: input value nano Ampere (nA)
    :param dict json_obj: complete record data object
    :param dict sensor_def:
    :param object: the device object:
    :return: o3 in ug/m3
    """
    device_id = record_in['device_id']
    T = None
    try:
        T = device.get_last_value(device_id, 'temperature', None)['value']
    except:
        pass

    no2 = None
    try:
        no2 = device.get_last_value(device_id, 'no2', None)['value']
    except:
        pass

    if T is None or no2 is None:
        return None

    return nano_ampere_o3_to_ugm3(device_id, nA, T, no2)
