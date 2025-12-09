# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class RefAttribute(models.Model):
    _inherit = "ref.attribute"

    tagging_ids = fields.Many2many(
        comodel_name="tagging.tags",
        relation="tagging_ref_attribute",
        column1="attribute_id",
        column2="tag_id",
        string="Tags",
    )
