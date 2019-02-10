import time
import dateutil.parser
from stetl.component import Config
from stetl.packet import FORMAT
from stetl.util import Util

from smartem.influxdbinput import InfluxDbInput

log = Util.get_log("HarvesterLastInfluxDbInput")


class HarvesterLastInfluxDbInput(InfluxDbInput):
    """
    InfluxDB TimeSeries Last Values fetcher/formatter.

    For now mainly used for AirSensEUR, later other devices may be supported.

    Algorithm, until time's up or all Measurements done:

        * fetch all Measurements (table names)
        * for each Measurement:
        * query all sample records for last 2 hours sorted by time descendent
        * get last record for each record (field 'name' is)
        * format to record that Refiner understands

    """

    @Config(ptype=str, default=None, required=True)
    def device_type(self):
        """
        The station/device type, e.g. 'ase'.

        Required: False

        Default: None
        """
        pass

    @Config(ptype=str, default=None, required=True)
    def device_version(self):
        """
        The station/device version, e.g. '1'.

        Required: False

        Default: None
        """
        pass

    @Config(ptype=dict, default=None, required=False)
    def meas_name_to_device_id(self):
        """
        How to map InfluxDB Measurement (table) names to SE device id's.
        e.g. {'Geonovum1' : '1181001', 'RIVM2' : '1181002'}

        Required: False

        Default: None
        """
        pass

    @Config(ptype=str, default='2h', required=False)
    def query_since(self):
        """
        What timespan to query upto now, using InfluxDB time format, e.g. 1h, 2h, 30m.

        Required: False

        Default: 2h
        """
        pass

    @Config(ptype=int, default=20, required=False)
    def query_limit(self):
        """
        Max records to return from query.

        Required: False

        Default: 20
        """
        pass

    def __init__(self, configdict, section, produces=FORMAT.record):
        InfluxDbInput.__init__(self, configdict, section, produces)
        self.current_time_secs = lambda: int(round(time.time()))
        self.start_time_secs = self.current_time_secs()
        self.measurements_info = []
        self.index_m = -1
        self.query = "SELECT * FROM %s WHERE time >= now()-%s and time <= now() ORDER BY time DESC LIMIT %d"

    def init(self):
        InfluxDbInput.init(self)

        # One time: get all measurements and related info and store in structure
        measurements = self.get_measurement_names()
        for measurement in measurements:
            # Optional mapping from MEASUREMENT name to a device id
            # Otherwise device_is is Measurement name
            device_id = measurement
            if self.meas_name_to_device_id:
                if measurement not in self.meas_name_to_device_id:
                    log.warn('No device_id mapped for measurement (table) %s' % measurement)
                    continue

                device_id = self.meas_name_to_device_id[measurement]

            # Shift time for current_ts from progress table if already in progress
            # otherwise use start time of measurement.

            # Store all info per device (measurement table) in list of dict
            self.measurements_info.append({
                'name': measurement,
                'device_id': device_id,
                'query': self.query % (measurement, self.query_since, self.query_limit)
            })

        print ("measurements_info: %s" % str(self.measurements_info))

    def all_done(self):
        return len(self.measurements_info) == 0

    def next_measurement_info(self):
        self.index_m += 1
        return self.measurements_info[self.index_m % len(self.measurements_info)]

    def del_measurement_info(self):
        if not self.all_done():
            del self.measurements_info[self.index_m % len(self.measurements_info)]

    def after_invoke(self, packet):
        # Remove last processed measurement from todolist
        self.del_measurement_info()

    def before_invoke(self, packet):
        if self.all_done():
            # All measurements done
            log.info('Processing halted: all Measurements done')
            packet.set_end_of_stream()
            return False

    def read(self, packet):
        measurement_info = self.next_measurement_info()
        data = self.query_db(measurement_info['query'])

        if len(data) >= 1:
            # Having data: scrub for only the last unique
            # sensor names.
            last_name_vals = dict()
            for d in data:
                if 'name' in d and d['name'] not in last_name_vals:
                    last_name_vals[d['name']] = d

            last_vals = list(last_name_vals.values())

            packet.data = self.format_data(int(measurement_info['device_id']), last_vals)

        return packet

    # Create record with timeseries values that Refiner understands
    def format_data(self, device_id, data):
        record = dict()

        # Timestamp of sample
        record['device_id'] = device_id
        record['device_name'] = 'station %d' % device_id
        record['device_type'] = self.device_type
        record['device_version'] = self.device_version
        record['complete'] = True
        record['last'] = True

        # active over the last N hours (now 2) implicit through query
        record['value_stale'] = 0

        # Time already as UTC string
        # e.g. u'2018-10-17T15:00:14.746Z'
        datetime_str = data[0]['time']
        record['time'] = dateutil.parser.parse(datetime_str)

        # Add sensor values data
        record['data'] = {
            'timeseries': data
        }

        return record
