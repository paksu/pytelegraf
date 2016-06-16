from utils import format_string, format_value
import copy
import socket


class Line(object):
    def __init__(self, measurement, values, tags={}, timestamp=None):
        assert measurement, "Must have measurement"
        assert values, "Must have values"

        # Name of the actual measurement
        self.measurement = measurement
        # Single value or a dict of value_name: value pairs
        self.values = values
        # Dict of tags if any
        self.tags = tags
        # User provided timestamp if any
        self.timestamp = timestamp

    def get_output_measurement(self):
        """
        Formats and escapes measurement name that can be rendered to line protocol
        """
        return format_string(self.measurement)

    def get_output_values(self):
        """
        Return an escaped string of comma separated value_name: value pairs
        """
        if not isinstance(self.values, dict):
            values = {'value': self.values}
        else:
            values = self.values

        return ",".join("{0}={1}".format(format_string(k), format_value(v)) for k, v in values.items())

    def get_output_tags(self):
        """
        Return an escaped string of comma separated tag_name: tag_value pairs
        """
        return ",".join("{0}={1}".format(format_string(k), format_string(v)) for k, v in self.tags.items())

    def get_output_timestamp(self):
        """
        Formats timestamp so it can be rendered to line protocol
        """
        return " {}".format(self.timestamp) if self.timestamp else ""

    def to_line_protocol(self):
        """
        Converts the given metrics as a single line of InfluxDB line protocol
        """
        tags = self.get_output_tags()

        return "{}{} {}{}".format(
            self.get_output_measurement(),
            "," + tags if tags else '',
            self.get_output_values(),
            self.get_output_timestamp()
        )


class TelegrafClient(object):

    def __init__(self, host='localhost', port=8094, tags={}):
        self.host = host
        self.port = port
        self.tags = tags
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write(self, series_name, values, tags={}, timestamp=None):
        """
        Append global tags to the data given and send it
        """
        all_tags = copy.copy(self.tags)
        all_tags.update(tags)

        line = Line(series_name, values, all_tags, timestamp)
        self.send(line.to_line_protocol())

    def send(self, data):
        try:
            self.socket.sendto(data.encode('ascii'), (self.host, self.port))
        except (socket.error, RuntimeError):
            pass
