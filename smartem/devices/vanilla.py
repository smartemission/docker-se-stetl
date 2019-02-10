# -*- coding: utf-8 -*-
#
# Vanilla ('vanilla') Device implementation.
# A Vanilla device does not need any specialized
# processing. All data is already formatted and calibrated.
# An example is Luftdaten.info data.
#
# Author: Just van den Broecke - 2019+

import logging
from device import Device
from vanilladefs import SENSOR_DEFS

log = logging.getLogger('VanillaDevice')


class Vanilla(Device):

    def __init__(self):
        Device.__init__(self, 'vanilla')
        self.config_dict = None
        self.last_values = {}

    def init(self, config_dict):

        self.config_dict = config_dict

    def exit(self):
        pass

    def can_resolve(self, sensor_name, val_dict):
        sensor_def = self.get_sensor_def(sensor_name)
        if not sensor_def:
            return False
        return True

    def get_sensor_defs(self):
        return SENSOR_DEFS

    def get_sensor_meta_id(self, sensor_name, val_dict):
        if 'meta_id' in val_dict:
            return val_dict['meta_id']
        return self.get_sensor_def(sensor_name)['meta_id']

    # Get raw sensor value or list of values
    def get_raw_value(self, name, val_dict):
        if name not in val_dict:
            return None, name

        val = val_dict[name]

        return val, name

    # Check for valid sensor value
    def check_value(self, name, val_dict, value=None):

        if name not in val_dict:
            return False, '%s not in val_dict' % name

        if name not in SENSOR_DEFS:
            return False, '%s not in SENSOR_DEFS' % name

        name_def = SENSOR_DEFS[name]
        val = val_dict[name]

        if 'min' in name_def and val < name_def['min']:
            return False, '%s: val(%s) < min(%s)' % (name, str(val), str(name_def['min']))

        if 'max' in name_def and val > name_def['max']:
            return False, '%s: val(%s) > max(%s)' % (name, str(val), str(name_def['max']))

        return True, '%s OK' % name

    def get_last_value(self, device_id, name, val_dict):
        try:
            # Best effort
            # TODO check for timestamps (not too long ago)
            return self.last_values[str(device_id)][name]
        except:
            pass
        return None

    def set_last_value(self, device_id, name, value, val_dict):
        try:
            # Best effort
            device_id = str(device_id)
            if device_id not in self.last_values:
                self.last_values[device_id] = {}

            if name not in self.last_values[device_id]:
                self.last_values[device_id][name] = {}

            self.last_values[device_id][name]['value'] = value
            if 'time' in val_dict:
                self.last_values[device_id][name]['time'] = val_dict['time']
        except:
            pass
