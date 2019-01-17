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

TWO_POW_16 = 65536.0
TEN_POW_9 = float(pow(10, 9))


# Equation 1: [1] page 3
# STEP 1 Digital to Voltage (V)
# V = (Ref - RefAD) + (Digital+1) /2^16 x 2 x RefAD
# STEP 2 Voltage (V) to Ampere (I) as Ri
# I = 10^9 V/(Gain x Rload)
def digital2nanoAmpere(value, device, sensor_name):
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
def rec_digital2nanoAmpere(value, record_in=None, sensor_def=None, device=None):
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

    return digital2nanoAmpere(value, device, sensor_name)


