# Calibration test ASE-NL devices
import sys
from airsenseur import AirSensEUR
from airsenseurparms import ASE_PARMS

# Rs=a0+a1*NO2+a2*T
# Rs - a0 - a2T = a1 * NO2
# NO2 = (Rs - a0 - a2T ) / a1


#
# [2] https://www.samenmetenaanluchtkwaliteit.nl/sites/default/files/2017-12/Jan%20Vonk_AirSensEUR.pptx.pdf
# Jan Vonk - RIVM
#

TWO_POW_16 = float(pow(2, 16))
TEN_POW_3 = float(pow(10, 3))
TEN_POW_6 = float(pow(10, 6))
TEN_POW_9 = float(pow(10, 9))


# Equation 1: [1] page 3
# V = (Vref - RefAD) + DigitalReading * 2 *  RefAD / 2**16
# The sensor output is in digitalised values between 0 and 65535, using a 16 bit analogue to digital converter.
# The procedure to compute the current is:
# 1: the digital values are converted to volt using equation :
#       V = (Ref - RefAD) + (DigitalValues+1)/2^16 * 2 * RefAD, V is in Volt with RefAD = 0.5 V
# and Ref = 1.7 V, 1.50 V, 1.7 V and 1.2 V
#      for NO2, CO, O3 and CO sensors, respectively.
#      2. Then voltages shall be converted into current with equation :
#      I = 10^9 * V/ (Gain * RLoad) in nA with Gain = 7001, RLoad = 50 Ohms
#      The Ref, RefAD, Gain and RLoad values may change for other type of sensors or with new shield configurations.
#      I have added the first section of the report, to explain the conversion to current in the attached report.
#

def bits2volt(value, sensor_name, device):
    """
    Convert (evaluated) bits value to millivolt according to Vref and RefAD ASE formulas.

    :param int value: input value raw 2 byte number 0..65535
    :param dict json_obj: complete record data object
    :param dict sensor_def:
    :param object: the device object:
    :return:
    """
    # e.g. 'NO2-B43F'
    input_def = device.get_sensor_def(sensor_name)
    params = input_def['params']
    # Ref = 1.7 V, 1.50 V, 1.7 V and 1.2 V
    # for NO2, CO, O3 and CO sensors, respectively.
    v_ref = params['v_ref']
    v_ref_ad = params['v_ref_ad']

    # V = (Vref - RefAD) + value * 2 *  RefAD / 2**16
    # V = (Ref - RefAD) + (DigitalValues+1)/2^16 * 2 * RefAD, V is in Volt with RefAD = 0.5 V
    return (v_ref - v_ref_ad) + ((value + 1) / TWO_POW_16) * 2.0 * v_ref_ad

def example_NO2_ASE_NL01():
    # Example to test calculation in Python
    # For NO2B43F in ASE_NL_01 Sept 17, 2018 12:00
    # at RIVM Ref Station Breukelen

    # Constants
    TWO_POW_16 = 65536.0
    TEN_POW_9 = 1000000000.0

    Ref = 1.7
    RefAD = 0.5
    Gain = 7001.0
    RLoad = 50.0

    # Digital reading (minute value)
    # Sept 17, 2018 12:00 - ASE_NL_01 NO2B43F
    Digital = 61860.0
    RefRIVM = 48.0

    # STEP 1 Digital to Voltage (V)
    # V = (Ref - RefAD) + (Digital+1) /2^16 x 2 RefAD
    V = (Ref - RefAD) + (Digital+1) /TWO_POW_16 * 2.0 * RefAD
    # V = 2.14384765625

    # STEP 2 Voltage (V) to Ampere (I) as Ri
    # I = 10^9 V/(Gain x Rload)
    I = TEN_POW_9 * V/(Gain * RLoad)
    Ri = I
    # I = 6124.40410299

    # STEP 3 Per-sensor Linear equation NO2
    # Ri=a0+a1*NO2+a2*T
    # a0-a2 for ASE_NL01 NO2B43F (page 28)
    a0 = 6142.0
    a1 = -0.1479
    a2 = -0.1559
    T = 20.0
    no2 = ((Ri - a0 - a2 * T) / a1)
    print('Calibrated NO2 ug/m3=%f - RIVM hourly val=%d' % (no2, RefRIVM))
    # Calibrated NO2 ug/m3=96.416129 - RIVM hourly val=48

def example_NO_ASE_NL01():
    # Example to test calculation in Python
    # For NOB4 in ASE_NL_01 Sept 17, 2018 12:00
    # at RIVM Ref Station Breukelen

    # Constants
    TWO_POW_16 = 65536.0
    TEN_POW_9 = 1000000000.0

    Ref = 1.2
    RefAD = 0.5
    Gain = 7001.0
    RLoad = 50.0

    # Digital reading (minute value)
    # Sept 17, 2018 12:00 - ASE_NL_01 NOB4
    Digital = 9450.0

    # About 19-22 ug/m3
    RefRIVM = 19

    # STEP 1 Digital to Voltage (V)
    # V = (Ref - RefAD) + (Digital+1) /2^16 x 2 RefAD
    V = (Ref - RefAD) + (Digital+1) /TWO_POW_16 * 2.0 * RefAD
    # V = 2.14384765625

    # STEP 2 Voltage (V) to Ampere (I) as Ri
    # I = 10^9 V/(Gain x Rload)
    I = TEN_POW_9 * V/(Gain * RLoad)
    Ri = I
    # I = 6124.40410299

    # STEP 3 Per-sensor Linear equation (Polynominal on T CoV for NO)
    # Ri=a0+a1*NO+a2*T+ a3*T^2
    # a0-a3 for ASE_NL01 NOB4 (page 28)
    a0 = 2385.0
    a1 = 0.4851
    a2 = -1.574
    a3 = 0.1029
    T = 20.0
    no = ((Ri - a0 - a2 * T - a3 * T * T) / a1)
    print('Calibrated NO ug/m3=%f - RIVM hourly val=%d' % (no, RefRIVM))
    # Calibrated NO ug/m3=35.057462 - RIVM hourly val=19

if __name__ == '__main__':
    example_NO2_ASE_NL01()
    example_NO_ASE_NL01()
    
    # print(str(sys.argv))
    Digital = 61860
    ase = AirSensEUR()
    V = float(bits2volt(Digital, 'NO2B43F', ase))

    # I = 10^9 * V/ (Gain * RLoad) in nA with Gain = 7001, RLoad = 50 Ohms
    Gain = 7001.0
    RLoad = 50.0
    Ri = TEN_POW_9 * V/ (Gain * RLoad) 
    device_id = 11820001
    device_parms = ASE_PARMS[str(device_id)]
    a0 = device_parms['NO2']['a0']
    a1 = device_parms['NO2']['a1']
    a2 = device_parms['NO2']['a2']
    T = 20.0
    no2 = ((Ri - a0 - a2 * T) / a1)

    print('NO2 ug/m3=' + str(no2))
