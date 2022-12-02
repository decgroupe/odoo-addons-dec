# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class RefReference(models.Model):
    _inherit = 'ref.reference'
    _name = _inherit

    tagging_ids = fields.Many2many(
        comodel_name='tagging.tags',
        relation='tagging_ref_reference',
        column1='reference_id',
        column2='tag_id',
        string='Tags',
    )
