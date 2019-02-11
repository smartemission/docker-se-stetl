import json
from stetl.component import Config
from stetl.util import Util
from stetl.inputs.httpinput import HttpInput
from stetl.packet import FORMAT
from smartem.util.utc import zulu_to_gmt

log = Util.get_log("LuftdatenInput")


class LuftdatenInput(HttpInput):
    """
    Luftdaten.info API input abstract base class.

    For now mainly within one or more bbox-es, later other options.
    API doc: https://github.com/opendata-stuttgart/meta/wiki/APIs

    """

    @Config(ptype=str, default='vanilla', required=True)
    def device_type(self):
        """
        The station/device type, e.g. 'ase' or plain vanilla.

        Required: True

        Default: vanilla
        """
        pass

    @Config(ptype=str, default='1', required=True)
    def device_version(self):
        """
        The station/device version, e.g. '1'.

        Required: True

        Default: '1'
        """
        pass

    @Config(ptype=dict, default=None, required=False)
    def bboxes(self):
        """
        Which BBOXes to query or filter.
        e.g. {'Nijmegen': [5.6,51.7,6.0,51.9] }

        Required: False

        Default: None
        """
        pass

    def __init__(self, configdict, section, produces=FORMAT.record):
        HttpInput.__init__(self, configdict, section, produces)

    # Convert single LTD sensor item object to record.
    def sensor_item2record(self, sensor_item):
        # Handle single Luftdaten sensor entry
        # Examples:
        #     {
        #   "sensor": {
        #     "pin": "1",
        #     "id": 17622,
        #     "sensor_type": {
        #       "name": "SDS011",
        #       "id": 14,
        #       "manufacturer": "Nova Fitness"
        #     }
        #   },
        #   "timestamp": "2019-02-05 15:42:03",
        #   "location": {
        #     "latitude": "51.8600",
        #     "country": "NL",
        #     "id": 8930,
        #     "longitude": "5.8680",
        #     "altitude": "12.7"
        #   },
        #   "id": 2826167868,
        #   "sampling_rate": null,
        #   "sensordatavalues": [
        #     {
        #       "value_type": "P1",
        #       "id": 6003944572,
        #       "value": "30.00"
        #     },
        #     {
        #       "value_type": "P2",
        #       "id": 6003944573,
        #       "value": "23.50"
        #     }
        #   ]
        # },
        # {
        #   "sensor": {
        #     "pin": "7",
        #     "id": 17623,
        #     "sensor_type": {
        #       "name": "DHT22",
        #       "id": 9,
        #       "manufacturer": "various"
        #     }
        #   },
        #   "timestamp": "2019-02-05 15:42:04",
        #   "location": {
        #     "latitude": "51.8600",
        #     "country": "NL",
        #     "id": 8930,
        #     "longitude": "5.8680",
        #     "altitude": "12.7"
        #   },
        #   "id": 2826167908,
        #   "sampling_rate": null,
        #   "sensordatavalues": [
        #     {
        #       "value_type": "humidity",
        #       "id": 6003944658,
        #       "value": "47.80"
        #     },
        #     {
        #       "value_type": "temperature",
        #       "id": 6003944657,
        #       "value": "16.00"
        #     }
        #   ]
        # },
        # {
        #   "sensor": {
        #     "pin": "11",
        #     "id": 17624,
        #     "sensor_type": {
        #       "name": "BME280",
        #       "id": 17,
        #       "manufacturer": "Bosch"
        #     }
        #   },
        #   "timestamp": "2019-02-05 15:42:04",
        #   "location": {
        #     "latitude": "51.8600",
        #     "country": "NL",
        #     "id": 8930,
        #     "longitude": "5.8680",
        #     "altitude": "12.7"
        #   },
        #   "id": 2826167952,
        #   "sampling_rate": null,
        #   "sensordatavalues": [
        #     {
        #       "value_type": "humidity",
        #       "id": 6003944753,
        #       "value": "100.00"
        #     },
        #     {
        #       "value_type": "pressure",
        #       "id": 6003944755,
        #       "value": "102745.94"
        #     },
        #     {
        #       "value_type": "temperature",
        #       "id": 6003944749,
        #       "value": "4.06"
        #     },
        #     {
        #       "value_type": "pressure_at_sealevel",
        #       "value": 102906.83
        #     }
        #   ]
        # },
        record = dict()
        try:
            # sensor item: 4 main entries:
            location = sensor_item['location']
            sensor = sensor_item['sensor']
            sensordatavalues = sensor_item['sensordatavalues']

            # "2019-02-05 15:42:04" make Zulu '2019-02-05T15:42:04Z'
            timestamp = sensor_item['timestamp']
            timestamp = self.timestamp_to_gmt(timestamp)
            if not timestamp:
                return None

            kit_id = str(location['id'])
            device_id = int('4931%s' % kit_id)
            device_name = 'LTD_%s' % kit_id
            sensor_type_name = sensor['sensor_type']['name']
            sensor_id = sensor['id']
            sensor_meta = '%s-%d' % (sensor_type_name, sensor_id)
            unique_id = '%s-%s' % (device_name, sensor_meta)

            altitude = 0
            if 'altitude' in location:
                altitude = int(round(float(location['altitude'])))

            # We MUST have lat/lon, otherwise exception and skip.
            longitude = location['longitude']
            latitude = location['latitude']
            point = 'SRID=4326;POINT(%s %s)' % (longitude, latitude)

            # Build up the record with required fields
            # sensor data values will be in record['data']['timeseries']
            record['device_id'] = device_id
            record['device_name'] = device_name
            record['device_type'] = self.device_type
            record['device_meta'] = 'luftdaten-%s' % str(self.device_version)
            record['device_version'] = self.device_version
            record['unique_id'] = unique_id
            record['time'] = timestamp
            record['point'] = point
            record['altitude'] = altitude
            record['complete'] = True
            record['last'] = True
            record['value_stale'] = 0

            # Assemble sensor values into single 'data_item' dict
            data = list()
            unique_id = '%s-%s' % (device_name, sensor_meta)
            data_item = {
                'time': timestamp,
                'meta_id': '%s-%d' % (sensor_type_name, sensor_id),
                'unique_id': unique_id
            }
            for val in sensordatavalues:
                try:

                    indicator = val['value_type']
                    value = float(val['value'])

                    if indicator == 'P1':
                        indicator = 'pm10'
                    elif indicator == 'P2':
                        indicator = 'pm2_5'
                    elif indicator == 'pressure_at_sealevel':
                        continue
                    elif indicator == 'pressure':
                        value = value / 100.0

                    value = int(round(value))
                    data_item[indicator] = value
                except Exception as e:
                    log.warn('Error id=%s, err= %s' % (unique_id, str(e)))
                    continue

            if len(data_item.values()) == 0:
                return None

            # Add sensor values data
            data.append(data_item)
            record['data'] = {
                'timeseries': data
            }
        except Exception as e:
            log.warn('Error val=%s, err= %s' % (str(sensor_item), str(e)))
            record = None

        return record

    def parse_json_str(self, raw_str):
        # Parse JSON from data string
        json_obj = None
        try:
            json_obj = json.loads(raw_str)
        except Exception as e:
            log.error('Cannot parse JSON from %s, err= %s' % (raw_str, str(e)))
            raise e

        return json_obj

    def timestamp_to_gmt(self, timestamp):
        if not timestamp:
            return None

        ts_gmt = None
        try:
            ts_parts = timestamp.split(' ')
            ts_zulu = '%sT%sZ' % (ts_parts[0], ts_parts[1])
            ts_gmt = zulu_to_gmt(ts_zulu)
        except Exception as e:
            log.warn('Error timestamp_to_gmt id=%s e=%s' % (timestamp, str(e)))
        return ts_gmt

    def next_entry(self, a_list):
        if len(a_list) == 0:
            return None

        return a_list.pop(0)
