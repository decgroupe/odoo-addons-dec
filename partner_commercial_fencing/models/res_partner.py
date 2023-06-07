# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    inherit_commercial_partner = fields.Boolean(
        string="Inherit commercial contact from the parent/company",
        default=True,
        help="If unchecked, then this partner will not be able to see "
        "business documents from its commercial partner.",
    )

    unfenced_commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_commercial_partner",
        string="Unfenced Commercial Entity",
        store=True,
        index=True,
    )

    @api.depends(
        "is_company",
        "inherit_commercial_partner",
        "parent_id.inherit_commercial_partner",
    )
    def _compute_commercial_partner(self):
        super()._compute_commercial_partner()
        for rec in self:
            rec.unfenced_commercial_partner_id = rec.commercial_partner_id
            if not rec.inherit_commercial_partner and not rec.is_company:
                rec.commercial_partner_id = rec
