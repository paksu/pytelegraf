from telegraf.client import TelegrafClient, HttpClient
from telegraf.protocol import Line
from telegraf.utils import format_string, format_value
import unittest
import mock


class TestLine(unittest.TestCase):

    def test_format_key(self):
        self.assertEquals(format_string('foo'), 'foo')
        self.assertEquals(format_string('foo,bar'), 'foo\,bar')
        self.assertEquals(format_string('foo bar'), 'foo\ bar')
        self.assertEquals(format_string('foo ,bar'), 'foo\ \,bar')

    def test_format_value(self):
        self.assertEquals(format_value('foo'), '"foo"')
        self.assertEquals(format_value('foo bar'), '"foo bar"')
        self.assertEquals(format_value('foo "and" bar'), '"foo \"and\" bar"')
        self.assertEquals(format_value(123), "123i")
        self.assertEquals(format_value(123.123), "123.123")
        self.assertEquals(format_value(True), "True")
        self.assertEquals(format_value(False), "False")

    def test_single_value(self):
        self.assertEquals(
            Line('some_series', 1).to_line_protocol(),
            'some_series value=1i'
        )

    def test_single_value_and_tags(self):
        self.assertEquals(
            Line('some_series', 1, {'foo': 'bar', 'foobar': 'baz'}).to_line_protocol(),
            'some_series,foo=bar,foobar=baz value=1i'
        )

    def test_multiple_values(self):
        self.assertEquals(
            Line('some_series', {'value': 232.123, 'value2': 123}).to_line_protocol(),
            'some_series value=232.123,value2=123i'
        )

    def test_multiple_values_and_tags(self):
        self.assertEquals(
            Line('some_series', {'value': 232.123, 'value2': 123}, {'foo': 'bar', 'foobar': 'baz'}).to_line_protocol(),
            'some_series,foo=bar,foobar=baz value=232.123,value2=123i'
        )

    def test_tags_and_measurement_with_whitespace_and_comma(self):
        self.assertEquals(
            Line(
                'white space',
                {'value, comma': "foo"},
                {'tag with, comma': 'hello, world'}
            ).to_line_protocol(),
            """white\ space,tag\ with\,\ comma=hello\,\ world value\,\ comma="foo\""""
        )

    def test_boolean_value(self):
        self.assertEquals(
            Line('some_series', True).to_line_protocol(),
            'some_series value=True'
        )

    def test_value_escaped_and_quoted(self):
        self.assertEquals(
            Line('some_series', 'foo "bar"').to_line_protocol(),
            'some_series value="foo \"bar\""'
        )

    def test_with_timestamp(self):
        self.assertEquals(
            Line('some_series', 1000, timestamp=1234134).to_line_protocol(),
            'some_series value=1000i 1234134'
        )

    def test_tags_ordered_properly(self):
        self.assertEquals(
            Line('some_series', 1, {'a': 1, 'baa': 1, 'AAA': 1, 'aaa': 1}).to_line_protocol(),
            'some_series,AAA=1,a=1,aaa=1,baa=1 value=1i'
        )

    def test_values_ordered_properly(self):
        self.assertEquals(
            Line('some_series', {'a': 1, 'baa': 1, 'AAA': 1, 'aaa': 1}).to_line_protocol(),
            'some_series AAA=1i,a=1i,aaa=1i,baa=1i'
        )


class TestTelegraf(unittest.TestCase):
    def setUp(self):
        self.host = 'host'
        self.port = 1234
        self.addr = (self.host, self.port)

    def test_sending_to_socket(self):
        self.client = TelegrafClient(self.host, self.port)
        self.client.socket = mock.Mock()

        self.client.metric('some_series', 1)
        self.client.socket.sendto.assert_called_with(b'some_series value=1i\n', self.addr)
        self.client.metric('cpu', {'value_int': 1}, {'host': 'server-01', 'region': 'us-west'})
        self.client.socket.sendto.assert_called_with(b'cpu,host=server-01,region=us-west value_int=1i\n', self.addr)

    def test_global_tags(self):
        self.client = TelegrafClient(self.host, self.port, tags={'host': 'host-001'})
        self.client.socket = mock.Mock()

        self.client.metric('some_series', 1)
        self.client.socket.sendto.assert_called_with(b'some_series,host=host-001 value=1i\n', self.addr)

        self.client.metric('some_series', 1, tags={'host': 'override-host-tag'})
        self.client.socket.sendto.assert_called_with(b'some_series,host=override-host-tag value=1i\n', self.addr)


class TestTelegrafHttp(unittest.TestCase):
    def setUp(self):
        self.host = 'host'
        self.port = 1234
        self.url = 'http://{host}:{port}/write'.format(host=self.host, port=self.port)

    def test_sending_to_http(self):
        self.client = HttpClient(self.host, self.port)
        self.client.future_session = mock.Mock()

        self.client.metric('some_series', 1)
        self.client.future_session.post.assert_called_with(url=self.url, data='some_series value=1i')
        self.client.metric('cpu', {'value_int': 1}, {'host': 'server-01', 'region': 'us-west'})
        self.client.future_session.post.assert_called_with(url=self.url,
                                                           data='cpu,host=server-01,region=us-west value_int=1i')

    def test_global_tags(self):
        self.client = HttpClient(self.host, self.port, tags={'host': 'host-001'})
        self.client.future_session = mock.Mock()

        self.client.metric('some_series', 1)
        self.client.future_session.post.assert_called_with(data='some_series,host=host-001 value=1i', url=self.url)

        self.client.metric('some_series', 1, tags={'host': 'override-host-tag'})
        self.client.future_session.post.assert_called_with(data='some_series,host=override-host-tag value=1i',
                                                           url=self.url)
