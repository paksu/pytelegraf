from telegraf.protocol import Line
import copy
import socket


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
        """
        Sends the given data to the socket via UDP
        """
        try:
            self.socket.sendto(data.encode('ascii'), (self.host, self.port))
        except (socket.error, RuntimeError):
            # Socket errors should fail silently so they don't affect anything else
            pass
