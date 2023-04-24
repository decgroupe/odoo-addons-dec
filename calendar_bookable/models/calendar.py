# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = "calendar.event"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(Meeting, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
        if self._context.get("bookable") and not limit and not count:
            start_arg = False
            stop_arg = False
            for arg in args:
                if arg and len(arg) == 3:
                    if arg[0] == "start":
                        start_arg = arg
                    if arg[0] == "stop":
                        stop_arg = arg

            if start_arg and stop_arg:
                bookable_args = [
                    start_arg,
                    stop_arg,
                    ("partner_ids.bookable", "=", True),
                ]
                res |= super(Meeting, self).search(
                    bookable_args,
                    offset=offset,
                    limit=limit,
                    order=order,
                    count=count,
                )
        return res
