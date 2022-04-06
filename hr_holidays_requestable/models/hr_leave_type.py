# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

from odoo import api, models, fields


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    requestable_from = fields.Date(
        string="Requestable from",
        help="Date from which this type is requestable",
    )
    requestable_from_valid = fields.Boolean(
        string="Requestable",
        compute="_compute_requestable_from_valid",
        store=True,
        help="This indicates if it is possible to request this type of leave "
        "even when not valid",
    )

    @api.multi
    @api.depends("requestable_from", "validity_stop")
    def _compute_requestable_from_valid(self):
        dt = self._context.get('default_date_from'
                              ) or fields.Date.context_today(self)
        for rec in self:
            if rec.requestable_from and rec.validity_stop:
                rec.requestable_from_valid = (
                    (dt <= rec.validity_stop) and (dt >= rec.requestable_from)
                )
            else:
                rec.requestable_from_valid = False
