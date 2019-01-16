#
# Per-sensor parameters for raw value to mg/m3 conversion.
#
#

# Linear Equation Models:
# CO: Rs=a0+a1*CO+a2*RH
# NO: Rs=a0+a1*NO+a2*T + a3*T*T
# NO2: Rs=a0+a1*NO2+a2*T
# O3: Rs=a0+a1*O3+a2*NO2(sensor)+a3* T

# Example for NO2:
# Rs=a0+a1*NO2+a2*T
# Rs - a0 - a2T = a1 * NO2
# NO2 = (Rs - a0 - a2T ) / a1


ASE_PARMS = {
    '11820001':
        {
            'CO': {
                'a0': 3107,
                'a1': 0.2113,
                'a2': 0.2448,
            },
            'NO': {
                'a0': 2385,
                'a1': 0.4851,
                'a2': -1.574,
                'a3': 0.1029,
            },
            'NO2': {
                'a0': 6142,
                'a1': -0.1479,
                'a2': -0.1559,
            },
            'O3': {
                'a0': 6135,
                'a1': -0.2636,
                'a2': -0.2597,
                'a3': 0.1249,
            },
        }
}
