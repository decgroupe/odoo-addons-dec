# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import fields


class Bench:
    def __init__(self):
        """Create instance of Bench class."""
        self.start_time = float("nan")
        self.stop_time = float("nan")
        self.total_seconds = 0
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

    def start(self):
        """Start the timer."""
        self.start_time = fields.Datetime.now()
        return self

    def stop(self):
        """
        Report time elapsed since last call to start().
        """
        self.stop_time = fields.Datetime.now()

        # https://stackoverflow.com/questions/538666/format-timedelta-to-string
        self.total_seconds = (self.stop_time - self.start_time).total_seconds()
        self.hours, remainder = divmod(self.total_seconds, 3600)
        self.minutes, self.seconds = divmod(remainder, 60)
        return self

    def duration(self):
        """
        Return time elapsed.
        """
        res = "{:02}:{:02}:{:02}".format(
            int(self.hours),
            int(self.minutes),
            int(self.seconds),
        )
        return res

    # def __enter__(self):
    #     """Start the timer when using TicToc in a context manager."""
    #     self.start = default_timer()

    # def __exit__(self, *args):
    #     """On exit, pring time elapsed since entering context manager."""
    #     self.end = default_timer()
    #     self.elapsed = self.end - self.start
    #     print('Elapsed time is %f seconds.' % self.elapsed)
