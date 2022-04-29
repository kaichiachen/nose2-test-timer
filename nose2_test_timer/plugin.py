#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Kaichia Chen
# Created Date: Tue April 26 19:03:19 PDT 2022

__author__      = "Kaichia Chen"
__copyright__   = "Copyright 2022, Kaichia Chen"
__license__ = "MIT"

import json
import os
import re
import timeit

from nose2 import result
from nose2.events import Plugin

from collections import OrderedDict

try:
    import colorama
    TERMCOLOR2COLORAMA = {
        'green': colorama.Fore.GREEN,
        'yellow': colorama.Fore.YELLOW,
        'red': colorama.Fore.RED,
    }
except ImportError:
    colorama = None

# define constants
IS_NT = os.name == 'nt'

def _colorize(val, color):
    """Colorize a string through colorama"""
    if colorama is not None and color is not None:
        val = TERMCOLOR2COLORAMA[color] + val + colorama.Style.RESET_ALL

    return val


class TimerPlugin(Plugin):
    """This plugin provides test timings"""

    def __init__(self):
        """Initialize default argument"""

        self._timed_tests = {}
        self.timer_threshold = None
        self.json_file = None
        self.timer_ok = 5
        self.timer_warning = 10
        self.timer_top_n = -1
        self.timer_color = False
        self.timer_typefilter = None
        self._outcome = ''
        if self.session:
            self.options()

    def set_timer_enable(self, value):
        self.register()

    def set_json_file(self, value):
        self.json_file = value[0]

    def set_timer_top_n(self, value):
        self.timer_top_n = int(value[0])

    def set_timer_color(self, value):
        self.timer_color = True

    def set_timer_threshold(self, value):
        self.timer_threshold = float(value[0])

    def set_timer_warning(self, value):
        self.timer_warning = float(value[0])

    def set_timer_ok(self, value):
        self.timer_ok = float(value[0])

    def set_timer_typefilter(self, value):
        self.timer_typefilter = value[0].split(',')

    def _time_taken(self, start_time):
        return timeit.default_timer() - start_time

    def _get_result_color(self, time_taken):
        """Get time taken result color."""

        time_taken_ms = time_taken * 1000
        if time_taken_ms <= self.timer_ok * 1000:
            color = 'green'
        elif time_taken_ms <= self.timer_warning * 1000:
            color = 'yellow'
        else:
            color = 'red'

        return color

    def _colored_time(self, time_taken, color=None):
        """Get formatted and colored string for a given time taken."""

        if not self.timer_color:
            return "{0:0.4f}s".format(time_taken)

        return _colorize("{0:0.4f}s".format(time_taken), color)

    def _color_status(self, status, color=None):
        """Get formatted and colored string for a given status."""
        if self.timer_color:
            if status == result.ERROR or status == result.FAIL:
                return _colorize(status, 'red')
            else:
                return _colorize(status, 'green')

        return status

    def _format_report_line(self, test, time_taken, color, status, percent):
        """Format a single report line."""

        return "[{0}] {3:04.2f}% {1}: {2}".format(
            self._color_status(status, color),
            test, self._colored_time(time_taken, color), percent
        )

    def register(self):
        super(TimerPlugin, self).register()

    def startTestRun(self, event):
        """Initializes a timer before starting a test."""
        self._timer = timeit.default_timer()

    def beforeSummaryReport(self, event):
        """Report the test times."""

        sorted_times = sorted(self._timed_tests.items(),
                   key=lambda item: item[1]['time'],
                   reverse=True)

        if self.json_file:
            dict_type = OrderedDict if self.timer_top_n else dict
            with open(self.json_file, 'w') as f:
                json.dump({'tests': dict_type((k, v) for k, v in sorted_times)}, f,
                          indent=4, sort_keys=True)

        total_time = sum([vv['time'] for kk, vv in sorted_times])

        event.stream.writeln('----------------------------------------------------------------------')

        idx = 0
        for idx, (test, time_and_status) in enumerate(sorted_times):
            time_taken = time_and_status['time']
            status = time_and_status['status']
            if self.timer_typefilter and status not in self.timer_typefilter:
                continue
            if idx < self.timer_top_n or self.timer_top_n == -1:
                color = self._get_result_color(time_taken)
                percent = 0 if total_time == 0 else time_taken / total_time * 100
                line = self._format_report_line(test,
                                                time_taken,
                                                color,
                                                status,
                                                percent)

                if self.timer_threshold:
                    if time_taken >= self.timer_threshold:
                        event.stream.writeln(line)
                        idx += 1
                else:
                    event.stream.writeln(line)
                    idx += 1

    def testOutcome(self, event):
        """Handles test outcomes to register timings"""

        # No handlng for skipped tests yet
        if event.outcome == result.ERROR:
            self._outcome = event.outcome
        elif event.outcome == result.FAIL:
            self._outcome = event.outcome

    def setTestOutcome(self, event):
        self._outcome = event.outcome

    def startTest(self, event):
        test = event.test
        self._timed_tests[test.id()] = {
            'time': timeit.default_timer(),
        }

    def stopTest(self, event):
        test = event.test
        if test.id() in self._timed_tests:
            time_taken = self._time_taken(self._timed_tests[test.id()]['time'])
            self._timed_tests[test.id()]['time'] = time_taken
            self._timed_tests[test.id()]['status'] = self._outcome

    def options(self, env=os.environ):
        """Register commandline options."""

        # timer plugin switch
        self.addFlag(
            callback=self.set_timer_enable,
            short_opt='',
            long_opt="with-timer",
            help_text=(
                "Set this flag to enable nose2 timer plugin"
            ),
        )

        # timer top n
        self.addArgument(
            callback=self.set_timer_top_n,
            short_opt='',
            long_opt='timer-top-n',
            help_text=(
                "When the timer plugin is enabled, only show the top N tests that "
                "consume most of time. The default is -1, that means showing all tests."
            ),
        )

        # timer result file
        self.addArgument(
            callback=self.set_json_file,
            short_opt='',
            long_opt="timer-json-file",
            help_text=(
                "Save the results of the timing and status of each tests in "
                "said json file."
            ),
        )

        _time_units_help = ("Default time unit is a second, float type is acceptable")

        # timer ok threshold
        self.addArgument(
            callback=self.set_timer_ok,
            short_opt='',
            long_opt="timer-ok",
            help_text=(
                "Time result will be highlighted in green if xecution time smaller than input argument."
                "({units_help}).".format(units_help=_time_units_help)
            ),
        )

        # timer warning threshold
        self.addArgument(
            callback=self.set_timer_warning,
            short_opt='W',
            long_opt="timer-warning",
            help_text=(
                "Warning of execution time to highlight slow tests in "
                "yellow. Tests which take more time will be highlighted in "
                "red. ({units_help}).".format(units_help=_time_units_help)
            ),
        )

        # Windows + nosetests does not support colors (even with colorama).
        if not IS_NT:
            self.addFlag(
                callback=self.set_timer_color,
                short_opt='',
                long_opt="timer-color",
                help_text="Colorize output (useful for non-tty output).",
            )

        # timer filter threshold
        self.addArgument(
            callback=self.set_timer_threshold,
            short_opt='',
            long_opt="timer-threshold",
            help_text=(
                "Pick and show tests that exceed a threshold seconds. "
                "({units_help}).".format(units_help=_time_units_help)
            ),
        )

        # timer result type filter
        self.addArgument(
            callback=self.set_timer_typefilter,
            short_opt='',
            long_opt="timer-typefilter",
            help_text=(
                "Only output the specified type(passed, error, failed)."
                "Support multiple filter type separated with comma delimiter"
            ),
        )
