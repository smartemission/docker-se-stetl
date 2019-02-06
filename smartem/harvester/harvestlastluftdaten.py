import json
import time
from datetime import datetime, timedelta
from stetl.component import Config
from stetl.util import Util
from stetl.inputs.httpinput import HttpInput
from stetl.packet import FORMAT
from smartem.util.utc import zulu_to_gmt

log = Util.get_log("HarvesterLastLuftdatenInput")


class HarvesterLastLuftdatenInput(HttpInput):
    """
    Luftdaten.info Last Values fetcher/formatter.

    For now mainly within bbox, later other options.
    API doc: https://github.com/opendata-stuttgart/meta/wiki/APIs
    
    API Example all last 5 min measurements in greater Nijmegen area
    http://api.luftdaten.info/v1/filter/box=51.7,5.6,51.9,6.0
    One sensor:
    http://api.luftdaten.info/v1/sensor/17008/


    """

    @Config(ptype=int, default=0, required=False)
    def api_interval_secs(self):
        """
        The time in seconds to wait before invoking the RSA API again.

        Required: True

        Default: 0
        """
        pass


    @Config(ptype=dict, default=None, required=False)
    def bboxes(self):
        """
        Which BBOXes to query, default is all of Luftdaten.
        e.g. {'Nijmegen': [5.6,51.7,6.0,51.9] }

        Required: False

        Default: None
        """
        pass

    def __init__(self, configdict, section, produces=FORMAT.record_array):
        HttpInput.__init__(self, configdict, section, produces)

        # Init all bbox id's
        self.bboxes_vals = self.bboxes.values()
        self.bboxes_idx = 0
        self.bbox = None

        # Save the Base URL, specific URLs will be constructed in self.url later
        self.base_url = self.url
        self.url = None

    def init(self):
        pass

    def before_invoke(self, packet):
        """
        Called just before Component invoke.
        """

        # The base method read() will fetch self.url until it is set to None
        self.bbox, self.bboxes_idx = self.next_entry(self.bboxes_vals, self.bboxes_idx)

        # Stop when all bboxes done
        if self.bbox is None:
            self.url = None
            log.info('Processing halted: all bboxes done')
            packet.set_end_of_stream()
            # needs to continue such that further in the stream final actions
            # can be taken when stream is ending.
            # i.e. save calibration state at end of stream
            return True

        # ASSERT: still bbox(s) to be queried

        # Set the next "last values" URL for device and increment to next
        self.url = self.base_url + '/filter/box=%s' % ','.join(str(x) for x in self.bbox)

        return True

    def after_invoke(self, packet):
        """
        Called just after Component invoke.
        """

        # just pause to not overstress the RSA
        if self.api_interval_secs > 0:
            time.sleep(self.api_interval_secs)

        return True

    def exit(self):
        # done
        log.info('Exit')


    def read_from_url(self, url, parameters=None):
        """
        Read the data from the URL, override to catch Exception without exiting process.

        :param url: the url to fetch
        :param parameters: optional dict of query parameters
        :return:
        """
        # log.info('Fetch data from URL: %s ...' % url)

        try:
            data = HttpInput.read_from_url(self, url, parameters)
        except Exception as e:
            log.error('Error RawSensorAPIInput.read_from_url %s: e=%s, skip bbox...' % (url, str(e)))
            data = None

        # Everything is fine
        return data

    # Convert observations to array of records, one for each designated (see self.outputs) output
    def format_data(self, data):

        # Convert/split response into an array of device_output records

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
        # Output, record list of this def
        # CREATE TABLE smartem_rt.last_device_output (
        #   gid serial,
        #   unique_id character varying,
        #   insert_time timestamp with time zone default current_timestamp,
        #   device_id integer,
        #   device_name character varying,
        #   device_meta character varying,
        #   sensor_meta character varying,
        #   name character varying,
        #   label character varying,
        #   unit  character varying,
        #   time timestamp with time zone,
        #   value_raw integer,
        #   value_stale integer,
        #   value real,
        #   altitude integer default 0,
        #   point geometry(Point,4326),

        # If something went wrong
        if data is None:
            return None

        # Parse JSON from data string fetched by base method read()
        sensor_vals_list = self.parse_json_str(data)
        records = dict()
        for sensor_val in sensor_vals_list:
            try:
                location = sensor_val['location']
                kit_id = str(location['id'])
                device_id = int('4931%s' % kit_id)
                device_name = 'LTD_%s' % kit_id
                device_meta = 'luftdaten'
                sensor = sensor_val['sensor']
                sensor_type_name = sensor['sensor_type']['name']
                sensor_type_id = sensor['sensor_type']['id']
                sensor_meta = '%s-%d' % (sensor_type_name, sensor_type_id)
                unique_id = '%s-%s' % (device_name, sensor_meta)

                altitude = int(round(float(location['altitude'])))
                longitude = location['longitude']
                latitude = location['latitude']
                point = 'SRID=4326;POINT(%s %s)' % (longitude, latitude)

                sensordatavalues = sensor_val['sensordatavalues']
                for val in sensordatavalues:
                    try:
                        indicator = val['value_type']
                        sensor_meta = '%s-%d-%s' % (sensor_type_name, sensor_type_id, indicator)

                        value = float(val['value'])

                        unit = 'ug/m3'
                        label = 'unknown'
                        if indicator == 'P1':
                            indicator = 'pm10'
                            label = 'PM 10'
                        elif indicator == 'P2':
                            indicator = 'pm2_5'
                            label = 'PM 2.5'
                        elif indicator == 'pressure_at_sealevel':
                            continue
                        elif indicator == 'pressure':
                            value = value / 100.0
                            label = 'Luchtdruk'
                            unit = 'HectoPascal'
                        elif indicator == 'temperature':
                            unit = 'C'
                            label = 'Temperatuur'
                        elif indicator == 'humidity':
                            label = 'Luchtvochtigheid'
                            unit = 'Procent'
                        else:
                            log.warn('Unknown indicator: %s for kit_id=%s' % (indicator, kit_id))
                            
                        # "2019-02-05 15:42:04" make Zulu '2019-02-05T15:42:04Z'
                        timestamp = sensor_val['timestamp']
                        ts_parts = timestamp.split(' ')
                        timestamp_zulu = '%sT%sZ' % (ts_parts[0], ts_parts[1])
                        timestamp = zulu_to_gmt(timestamp_zulu)
                        if not timestamp:
                            continue
                            
                        value = int(round(value))
                        unique_id = '%s-%s-%s' % (device_name, sensor_meta, indicator)
                        record = dict()
                        record['unique_id'] = unique_id
                        record['device_id'] = device_id
                        record['device_name'] = device_name
                        record['device_meta'] = device_meta
                        record['sensor_meta'] = sensor_meta
                        record['name'] = indicator
                        record['label'] = label
                        record['unit'] = unit
                        record['time'] = timestamp
                        record['value'] = value
                        record['value_stale'] = 0
                        record['value_raw'] = value
                        record['point'] = point
                        record['altitude'] = altitude

                        records[unique_id] = record
                    except Exception as e:
                        log.warn('Error id=%s, err= %s' % (unique_id, str(e)))
                        continue
            except Exception as e:
                log.warn('Error val=%s, err= %s' % (str(sensor_val), str(e)))
                continue

        return records.values()

    def parse_json_str(self, raw_str):
        # Parse JSON from data string
        json_obj = None
        try:
            json_obj = json.loads(raw_str)
        except Exception as e:
            log.error('Cannot parse JSON from %s, err= %s' % (raw_str, str(e)))
            raise e

        return json_obj

    def next_entry(self, a_list, idx):
        if len(a_list) == 0 or idx >= len(a_list):
            idx = -1
            entry = None
        else:
            entry = a_list[idx]
            idx += 1

        return entry, idx
