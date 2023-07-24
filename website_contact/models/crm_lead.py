# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2023

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        string="Attachments",
        auto_join=True,
        domain=lambda self: [("res_model", "=", self._name)],
    )
