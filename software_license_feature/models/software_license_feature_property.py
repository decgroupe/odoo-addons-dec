# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021


from odoo import fields, models


class SoftwareLicenseFeatureProperty(models.Model):
    _name = "software.license.feature.property"
    _description = "Feature property for a software license"
    _rec_name = "name"
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
    )
    value_ids = fields.One2many(
        comodel_name="software.license.feature.value",
        inverse_name="property_id",
        string="Values",
    )
    customizable = fields.Boolean(
        string="Is Customizable ?",
        help="Indicate when this property is customizable when added in "
        "a feature set. That means that there will be no list of selectable "
        "values when customizable.",
    )
