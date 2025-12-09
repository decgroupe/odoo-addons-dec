# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021


from odoo import api, fields, models


class SoftwareLicenseFeatureValue(models.Model):
    _name = "software.license.feature.value"
    _description = "Value for a feature of a software license"

    property_id = fields.Many2one(
        comodel_name="software.license.feature.property",
        string="Feature",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )

    def _name_get(self):
        self.ensure_one()
        res = self.name
        # WARNING: This will also checks for request.session.debug
        if self.user_has_groups("base.group_no_one"):
            res = ("%s (%s)") % (res, self.property_id.name)
        return res

    @api.depends("name", "property_id.name")
    def name_get(self):
        result = []
        for rec in self:
            name = rec._name_get()
            result.append((rec.id, name))
        return result
