# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


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
