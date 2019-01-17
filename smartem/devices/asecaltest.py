# Calibration test ASE-NL devices
import sys
from airsenseur import AirSensEUR
from airsenseurparms import ASE_PARMS
from airsenseurdefs import digital2nanoAmpere

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
# For accurate computation, it is necessary to use the following values of Shield configuration:
#   name.sensor Sens.raw.unit  gas.sensor       RefAD        Ref         board.zero.set   GAIN   Rload
# 1     COA4            nA     Carbon_monoxide  0.5006105    1.500611    1.1003053        7001     50
# 3     NOB4            nA     Nitric_oxide     0.5000000    1.200244    0.8315018        7001     50
# 2     NO2B43F         nA     Nitrogen_dioxide 0.5006105    1.700855    2.1507937        7001     50
# 4     OX_A431         nA     Ozone            0.5006105    1.700855    2.1507937        7001     50


def example_NO_ASE_NL01():
    # Example to test calculation in Python
    # For NOB4 in ASE_NL_01 Sept 17, 2018 12:00
    # at RIVM Ref Station Breukelen

    # Constants
    TWO_POW_16 = 65536.0
    TEN_POW_9 = 1000000000.0

    Ref = 1.200244
    RefAD = 0.5006105
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
    # V = 0.844020396835

    # STEP 2 Voltage (V) to Ampere (I) as Ri
    # I = 10^9 V/(Gain x Rload)
    I = TEN_POW_9 * V/(Gain * RLoad)
    print('NO nA=' + str(I))
    Ri = I
    # I = 2411.14239919

    # STEP 3 Per-sensor Linear equation (Polynominal on T CoV for NO)
    # Ri=a0+a1*NO+a2*T+ a3*T^2
    # a0-a3 for ASE_NL01 NOB4 (page 28)
    a0 = 2384.5561239
    a1 = 0.4851297
    a2 = -1.573699
    a3 = 0.1028684
    T = 20.1
    no = ((Ri - a0 - a2 * T - a3 * T * T) / a1)
    print('Calibrated NO ug/m3=%f - RIVM hourly val=%d' % (no, RefRIVM))
    # Calibrated NO ug/m3=34.3367204745 - RIVM hourly val=19

def example_NO2_ASE_NL01():
    # Example to test calculation in Python
    # For NO2B43F in ASE_NL_01 Sept 17, 2018 12:00
    # at RIVM Ref Station Breukelen

    # Constants
    TWO_POW_16 = 65536.0
    TEN_POW_9 = 1000000000.0

    Ref = 1.700855
    RefAD = 0.5006105
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
    print('NO2 nA=' + str(I))
    Ri = I
    # I = 6124.40410299

    # STEP 3 Per-sensor Linear equation NO2
    # Ri=a0+a1*NO2+a2*T
    # a0-a2 for ASE_NL01 NO2B43F (page 28)
    a0 = 6141.5933846
    a1 = -0.1479105
    a2 = -0.1959212
    T = 20.1
    no2 = ((Ri - a0 - a2 * T) / a1)
    print('Calibrated NO2 ug/m3=%f - RIVM hourly val=%d' % (no2, RefRIVM))
    # Calibrated NO2 ug/m3=96.416129 - RIVM hourly val=48


if __name__ == '__main__':
    example_NO2_ASE_NL01()
    example_NO_ASE_NL01()
    
    ase = AirSensEUR()

    # NO2 test
    Digital = 61860.0
    RiNO2 = float(digital2nanoAmpere(Digital, ase, 'NO2B43F'))
    print('NO2 nA=' + str(RiNO2))

    # NO test
    Digital = 9450.0
    RiNO = float(digital2nanoAmpere(Digital, ase, 'NOB4'))
    print('NO nA=' + str(RiNO))

