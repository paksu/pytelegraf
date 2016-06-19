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

        # Order the values first
        value_order = sorted(values.keys(), key=str.lower)

        return ",".join("{0}={1}".format(format_string(value_name), format_value(values[value_name])) for value_name in value_order)

    def get_output_tags(self):
        """
        Return an escaped string of comma separated tag_name: tag_value pairs

        Tags should be sorted by key before being sent for best performance. The sort should
        match that from the Go bytes.Compare function (http://golang.org/pkg/bytes/#Compare).
        """

        # Order the tags first
        tag_order = sorted(self.tags.keys(), key=str.lower)

        return ",".join("{0}={1}".format(format_string(tag_name), format_string(self.tags[tag_name])) for tag_name in tag_order)

    def get_output_timestamp(self):
        """
        Formats timestamp so it can be rendered to line protocol
        """
        return " {0}".format(self.timestamp) if self.timestamp else ""

    def to_line_protocol(self):
        """
        Converts the given metrics as a single line of InfluxDB line protocol
        """
        tags = self.get_output_tags()

        return "{0}{1} {2}{3}".format(
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
