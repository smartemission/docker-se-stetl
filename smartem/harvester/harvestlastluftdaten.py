from stetl.util import Util
from stetl.inputs.httpinput import HttpInput
from stetl.packet import FORMAT
from luftdateninput import LuftdatenInput

log = Util.get_log("HarvesterLastLuftdatenInput")


class HarvesterLastLuftdatenInput(LuftdatenInput):
    """
    Luftdaten.info Last Values fetcher/formatter.

    For now mainly within one or more bbox-es, later other options.
    API doc: https://github.com/opendata-stuttgart/meta/wiki/APIs
    
    API Example all last 5 min measurements in greater Nijmegen area
    http://api.luftdaten.info/v1/filter/box=51.7,5.6,51.9,6.0
    One sensor:
    http://api.luftdaten.info/v1/sensor/17008/

    """

    def __init__(self, configdict, section, produces=FORMAT.record):
        LuftdatenInput.__init__(self, configdict, section, produces)

        # Init all bbox id's
        self.bboxes_vals = self.bboxes.values()
        self.bbox = None

        # Save the Base URL, specific URLs will be constructed in self.url later
        self.base_url = self.url
        self.url = None
        self.sensor_items = list()
        self.sensor_item = None

    def before_invoke(self, packet):
        """
        Called just before Component invoke.
        """

        if len(self.sensor_items) == 0:
            # The base method read() will fetch self.url until it is set to None
            self.bbox = self.next_entry(self.bboxes_vals)

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
            log.info('Next bbox to fetch: %s' % str(self.bbox))

            # Set the next "last values" URL for device and increment to next
            self.url = self.base_url + '/filter/box=%s' % ','.join(str(x) for x in self.bbox)

        return True

    def after_invoke(self, packet):
        """
        Called just after Component invoke.
        """

        # To prevent stopping after first read()
        self.url = self.base_url
        return True

    #  Allows multiple (virtual) reads (overridden from HttpInput)
    def read_from_url(self, url, parameters=None):
        """
        Read the data from the URL, override to catch Exception without exiting process.

        :param url: the url to fetch
        :param parameters: optional dict of query parameters
        :return:
        """

        if len(self.sensor_items) == 0:
            log.info('Fetch data from URL: %s ...' % url)

            try:
                data = HttpInput.read_from_url(self, url, parameters)
            except Exception as e:
                log.error('Error RawSensorAPIInput.read_from_url %s: e=%s, skip bbox...' % (url, str(e)))
                data = None

            if data is None:
                return None

            # Parse JSON from data string fetched by base method read()
            self.sensor_items = self.parse_json_str(data)

        self.sensor_item = self.next_entry(self.sensor_items)

        # Everything is fine
        return self.sensor_item

    # Format single LTD sensor item object to record (overridden from HttpInput).
    def format_data(self, sensor_item):
        # If something went wrong
        if sensor_item is None:
            return None
        return self.sensor_item2record(sensor_item)
