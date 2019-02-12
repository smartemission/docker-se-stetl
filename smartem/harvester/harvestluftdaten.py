import time
from datetime import datetime
import json
from stetl.util import Util
from stetl.packet import FORMAT
from luftdateninput import LuftdatenInput

log = Util.get_log("HarvesterLuftdatenInput")


class HarvesterLuftdatenInput(LuftdatenInput):
    """
    Luftdaten.info timeseries (last hour) Values fetcher/formatter.

    For now mainly within one or more bbox-es, later other options.
    API doc: https://github.com/opendata-stuttgart/meta/wiki/APIs
    
    API Example all last 5 min measurements in greater Nijmegen area
    http://api.luftdaten.info/v1/filter/box=51.7,5.6,51.9,6.0
    One sensor:
    http://api.luftdaten.info/v1/sensor/17008/

    Last hour average all sensors (no bbox query possible): is
    used here:
    http://api.luftdaten.info/static/v2/data.1h.json

    """

    def __init__(self, configdict, section, produces=FORMAT.record_array):
        LuftdatenInput.__init__(self, configdict, section, produces)
        self.current_time_secs = lambda: int(round(time.time()))

        # Init all bbox id's
        self.bboxes_vals = list()
        if self.bboxes:
            self.bboxes_vals = self.bboxes.values()

    # Format all LTD sensor item object to record (overridden from HttpInput).
    def assemble(self, sensor_items):

        device_records = dict()
        for sensor_item in sensor_items:
            location_id = 'unknown'
            try:
                for bbox in self.bboxes_vals:
                    # Single array of floats lowerleft (lat,lon), upperright (lat,lon)
                    location = sensor_item['location']
                    location_id = location['id']
                    longitude = float(location['longitude'])
                    latitude = float(location['latitude'])

                    # Test if this device is in bbox
                    if bbox[0] < latitude < bbox[2] and bbox[1] < longitude < bbox[3]:

                        sensor_record = self.sensor_item2record(sensor_item)
                        if not sensor_record:
                            log.warn('Error sensor_item2record location_id=%s - skipping' % str(location_id))
                            continue

                        device_name = sensor_record['device_name']

                        if device_name not in device_records:
                            # First occurrence of this station (kit)

                            log.info('Create new raw data record for device_name=%s' % device_name)
                            #

                            # Create record with JSON text blob with metadata
                            record = dict()
                            device_id = sensor_record['device_id']

                            # Timestamp (GMT) of sample
                            # d = sensor_record['time']
                            current_time_secs = self.current_time_secs()
                            d = datetime.utcfromtimestamp(current_time_secs)
                            day = int(d.strftime('%Y%m%d'))

                            # current hour is the previous hour for meas-averages
                            # hour 1 is from 00:00 to 01:00, 2 from 00:01 to 02:00 etc
                            # hour 23:00-00:00 is 24! See below.
                            hour = d.hour

                            # Yesterday last hour (23:00-00:00), also shift date (day) back
                            if hour == 0:
                                d = datetime.utcfromtimestamp(current_time_secs - 3600)
                                day = int(d.strftime('%Y%m%d'))
                                hour = 24

                            # -- Map this to
                            # CREATE TABLE smartem_raw.timeseries (
                            #   gid serial,
                            #   unique_id character varying not null,
                            #   insert_time timestamp with time zone default current_timestamp,
                            #   device_id integer not null,
                            #   day integer not null,
                            #   hour integer not null,
                            #   data json,
                            #   complete boolean default false,
                            #   device_type character varying not null default 'jose',
                            #   device_version character varying not null default '1',
                            #   PRIMARY KEY (gid)
                            # )
                            record['device_id'] = device_id
                            record['device_type'] = self.device_type
                            record['device_version'] = self.device_version
                            record['unique_id'] = '%s-%s-%s' % (str(device_id), str(day), str(hour))
                            record['day'] = day
                            record['hour'] = hour

                            # Determine if hour is "complete"
                            record['complete'] = True

                            # Add JSON text blob
                            for item in sensor_record['data']['timeseries']:
                                if 'time' in item:
                                    del (item['time'])

                                    # Need lat/long for every measurement!
                                    item['latitude'] = latitude
                                    item['longitude'] = longitude

                                log.info('Start timeseries for device_name=%s meta_id=%s' % (device_name, item['meta_id']))

                            # Start bulk data record, with all measurements of last hour
                            record['data'] = {
                                'id': device_id,
                                'date': day,
                                'hour': hour,
                                'timeseries': sensor_record['data']['timeseries']
                            }

                            device_records[device_name] = record
                        else:
                            record = device_records[device_name]
                            for item in sensor_record['data']['timeseries']:
                                if 'time' in item:
                                    del (item['time'])
                                    item['latitude'] = latitude
                                    item['longitude'] = longitude

                                # Append to other timeseries already in record
                                record['data']['timeseries'].append(item)

                                log.info('Appended timeseries for device_name=%s meta_id=%s' % (device_name, item['meta_id']))

            except Exception as e:
                log.warn('Error location_id=%s, err= %s' % (str(location_id), str(e)))
                continue

        records = device_records.values()
        for record in records:
            # Need json blob format for data field
            json_data = json.dumps(record['data'])
            record['data'] = json_data

        return records

    # Format all LTD sensor item object to record (overridden from HttpInput).
    def format_data(self, data):
        sensor_items = self.parse_json_str(data)
        records = self.assemble(sensor_items)
        return records
