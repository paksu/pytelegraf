from telegraf.protocol import Line
import socket


class TelegrafClient(object):

    def __init__(self, host='localhost', port=8094, tags=None):
        self.host = host
        self.port = port
        self.tags = tags or {}

        # Creating the socket immediately should be safe because it's UDP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def metric(self, measurement_name, values, tags=None, timestamp=None):
        """
        Append global tags configured for the client to the tags given then
        converts the data into InfluxDB Line protocol and sends to to socket
        """
        if not measurement_name or not values:
            # Don't try to send empty data
            return

        tags = tags or {}

        # Do a shallow merge of the metric tags and global tags
        all_tags = dict(self.tags, **tags)

        # Create a metric line from the input and then send it to socket
        line = Line(measurement_name, values, all_tags, timestamp)
        self.send(line.to_line_protocol())

    def send(self, data):
        """
        Sends the given data to the socket via UDP
        """
        try:
            self.socket.sendto(data.encode('ascii') + b'\n', (self.host, self.port))
        except (socket.error, RuntimeError):
            # Socket errors should fail silently so they don't affect anything else
            pass
