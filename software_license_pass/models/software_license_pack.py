# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SoftwareLicensePack(models.Model):
    _name = "software.license.pack"
    _description = "Application Pack"

    name = fields.Char(
        string="Name",
        translate=True,
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="software.license.pack.line",
        inverse_name="pack_id",
        string="Pack Content",
        help="Applications that are part of this pack.",
    )
    pass_ids = fields.One2many(
        comodel_name="software.license.pass",
        inverse_name="pack_id",
        string="Passes",
        help="Passes generated from this pack.",
    )
    pass_count = fields.Integer(
        compute="_compute_pass_count",
        string="Number of Passes",
    )

    def write(self, vals):
        _logger.info("Writing pack data")
        return super().write(vals)

    @api.depends("pass_ids")
    def _compute_pass_count(self):
        for rec in self:
            rec.pass_count = len(rec.pass_ids)

    def action_view_pass(self):
        return self.pass_ids.action_view()

    def action_resync(self):
        self.mapped("pass_ids").action_resync_with_pack()
