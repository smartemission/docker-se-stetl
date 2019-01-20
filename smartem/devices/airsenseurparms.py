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
            'co': {
                'a0': 3106.838,
                'a1': 0.2112824,
                'a2': 0.2448138,
            },
            'no': {
                'a0': 2384.5561239,
                'a1': 0.4851297,
                'a2': -1.573699,
                'a3': 0.1028684,
            },
            'no2': {
                'a0': 6141.5933846,
                'a1': -0.1479105,
                'a2': -0.1959212,
            },
            'o3': {
                'a0': 6134.694,
                'a1': -0.2636486,
                'a2': -0.2597192,
                'a3': 0.1249437,
            },
        }
}


def get_parms(device_id, component_name):
    try:
        return ASE_PARMS[str(device_id)][component_name]
    except:
        pass
    return None
