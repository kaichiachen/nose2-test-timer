import unittest

from nose2.tools import params
from nose2_test_timer import plugin

try:
    from unittest import mock
except ImportError:
    import mock

class TestTimerPlugin(unittest.TestCase):

    def setUp(self):
        super(TestTimerPlugin, self).setUp()
        self.plugin = plugin.TimerPlugin()
        self.plugin.enabled = True
        self.plugin.timer_ok = 1000
        self.plugin.timer_warning = 2000
        self.plugin.timer_color = True
        self.test_mock = mock.MagicMock(name='test')
        self.test_mock.id.return_value = 1

    @params(
        (0.0001, '\x1b[32m0.0001s\x1b[0m', 'green'),
        (1,      '\x1b[32m1.0000s\x1b[0m', 'green'),
        (1.0001, '\x1b[33m1.0001s\x1b[0m', 'yellow'),
        (2.00,   '\x1b[33m2.0000s\x1b[0m', 'yellow'),
        (2.0001, '\x1b[31m2.0001s\x1b[0m', 'red'),
        (3.00,   '\x1b[31m3.0000s\x1b[0m', 'red')
    )
    def test_colored_time(self, time_taken, expected, color):
        self.assertEqual(self.plugin._colored_time(time_taken, color), expected)

    @params(
        (0.0001, '0.0001s', 'green'),
        (1,      '1.0000s', 'green'),
        (1.0001, '1.0001s', 'yellow'),
        (2.00,   '2.0000s', 'yellow'),
        (2.0001, '2.0001s', 'red'),
        (3.00,   '3.0000s', 'red')
    )
    def test_no_color_option(self, time_taken, expected, color):
        self.plugin.timer_color = False
        self.assertEqual(self.plugin._colored_time(time_taken, color), expected)

