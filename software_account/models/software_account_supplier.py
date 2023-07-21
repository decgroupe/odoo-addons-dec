# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class SoftwareAccountSupplier(models.Model):
    _name = "software.account.supplier"
    _description = "Software Account supplier"
    _order = "id desc"

    name = fields.Text(
        string="Name",
        required=True,
    )
    image = fields.Binary(
        string="Image",
    )
    rules = fields.Text(
        string="Rules",
    )
