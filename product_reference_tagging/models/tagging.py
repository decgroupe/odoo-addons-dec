# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class TaggingTag(models.Model):
    _inherit = "tagging.tags"
    _name = _inherit

    reference_ids = fields.Many2many(
        comodel_name='ref.reference',
        relation='tagging_ref_reference',
        column1='tag_id',
        column2='reference_id',
        string='References',
    )

    attribute_ids = fields.Many2many(
        comodel_name='ref.attribute',
        relation='tagging_ref_attribute',
        column1='tag_id',
        column2='attribute_id',
        string='Attributes',
    )
