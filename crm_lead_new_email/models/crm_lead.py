# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    original_message_id = fields.Many2one(
        string="Original Message",
        comodel_name="mail.message",
        compute="_compute_original_message_id",
    )

    @api.depends("message_ids")
    def _compute_original_message_id(self):
        for rec in self:
            message_ids = rec.message_ids.filtered(lambda x: x.message_type == "email")
            if message_ids:
                rec.original_message_id = message_ids[0]
            else:
                rec.original_message_id = False

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}
        defaults = {}
        if msg_dict.get("body"):
            defaults["description"] = msg_dict.get("body")
        defaults.update(custom_values)
        return super().message_new(msg_dict, custom_values=defaults)
