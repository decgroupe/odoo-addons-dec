# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

from odoo import _, api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    inherit_commercial_partner = fields.Boolean(
        string='Inherit commercial contact from the parent/company',
        default=True,
        help="If unchecked, then this partner will not be able to see "
        "business documents from its commercial partner.",
    )

    @api.depends(
        'is_company', 'inherit_commercial_partner',
        'parent_id.inherit_commercial_partner'
    )
    def _compute_commercial_partner(self):
        super()._compute_commercial_partner()
        # for partner in self.filtered(lambda x: not x.is_company):
        for rec in self:
            if not rec.inherit_commercial_partner and not rec.is_company:
                rec.commercial_partner_id = rec
                # rec.commercial_partner_id = getattr(self, '_origin', self)
