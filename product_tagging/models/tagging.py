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
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models, _


class TaggingTag(models.Model):
    _inherit = "tagging.tags"
    _name = _inherit

    product_ids = fields.Many2many(
        comodel_name='product.template',
        relation='tagging_product',
        column1='tag_id',
        column2='product_id',
        string='Products',
    )

    @api.model
    def search_tagproduct(self):
        self.env.cr.execute('SELECT '\
                        'tagging_tags.name, '\
                        'COUNT(tagging_tags.name) as tagscount '\
                    'FROM '\
                        'tagging_tags, '\
                        'tagging_product '\
                    'WHERE '\
                        'tagging_product.tag_id = tagging_tags.id '\
                    'GROUP BY '\
                        'tagging_tags.name, '\
                        'tagging_tags.id '\
                    'ORDER BY tagscount ')

        return self.env.cr.fetchall()
