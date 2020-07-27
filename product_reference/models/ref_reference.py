# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class RefReference(models.Model):
    """ Description """

    _name = 'ref.reference'
    _description = 'Reference'
    _rec_name = 'value'
    _order = 'value'

    category_id = fields.Many2one(
        'ref.category',
        'Category',
        required=True,
        oldname='category',
    )
    product_id = fields.Many2one(
        'product.template',
        'Product',
        required=True,
        oldname='product',
    )
    public_code = fields.Char(
        related='product_id.public_code',
        string='Public Code',
        oldname='product_ciel_code',
    )
    name = fields.Char(
        related='product_id.name',
        string='Name',
        oldname='product_name',
    )
    state = fields.Selection(
        related='product_id.state',
        string='Status',
        oldname='product_state',
    )
    internal_notes = fields.Text(
        related='product_id.internal_notes',
        string='Internal Notes',
        oldname='product_comments',
    )
    current_version = fields.Integer(
        'Current version',
        required=True,
    )
    value = fields.Text(
        'Value',
        required=True,
    )
    searchvalue = fields.Text(
        'Search value',
        required=True,
    )
    datetime = fields.Datetime(
        'Create date', required=True, default=fields.Datetime.now
    )
    folder_count = fields.Integer('Product folder item count')
    folder_error = fields.Integer('Product folder error count')
    folder_warning = fields.Integer('Product folder warning count')
    folder_task = fields.Integer('Product folder task count')
    picturepath = fields.Text('Path to picture')

    reference_line_ids = fields.One2many(
        'ref.reference.line',
        'reference_id',
        string='Lines',
        oldname='reference_lines',
    )
    version_ids = fields.One2many(
        'ref.version',
        'reference_id',
        string='Versions',
        oldname='version_lines',
    )
    price_ids = fields.One2many(
        'ref.price',
        'reference_id',
        string='Prices',
        oldname='price_lines',
    )

    _sql_constraints = [
        ('value_uniq', 'unique(value)', 'Reference value must be unique !'),
    ]

    @api.model
    def create(self, values):
        product_id = values.get('product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            product.mrp_production_request = True
        reference = super().create(values)
        return reference

    @api.model
    def search_custom(self, keywords):
        res = []
        for key in keywords[0]:
            if key and key[0] == '+':
                use_internal_notes = True
                key = key[1:]
            else:
                use_internal_notes = False

            if key:
                search_value = self.search([('searchvalue', 'ilike', key)]).ids
                search_category = self.search(
                    [('category_id.name', 'ilike', key)]
                ).ids
                search_name = self.search(
                    [('product_id.name', 'ilike', key)]
                ).ids
                search_ciel = self.search(
                    [('product_id.public_code', '=', key)]
                ).ids

                if use_internal_notes:
                    search_internal_notes = self.search(
                        [('product_id.internal_notes', 'ilike', key)]
                    ).ids
                else:
                    search_internal_notes = []

                if len(key) > 2:
                    search_tags = self.search(
                        [('product_id.tagging_ids.name', 'ilike', key)]
                    ).ids
                else:
                    search_tags = []

                res = res + search_value + search_category + search_name + search_internal_notes + search_ciel + search_tags

        return res

    @api.multi
    def run_material_cost_scheduler(self):
        MrpBom = self.env['mrp.bom']
        RefPrice = self.env['ref.price']

        for reference in self.search([]):
            if reference.category_id.code in ['ADT']:
                continue
            #_logger.info("Reference category name is {0}".format(reference.category_id.name))
            data = {}
            cost_price = 0.0
            if reference.product_id and reference.product_id.bom_ids:
                bom_id = MrpBom._bom_find(product_tmpl=reference.product_id)
                if bom_id:
                    _logger.info(
                        'Compute material cost price for [%s] %s',
                        reference.value, reference.product_id.name
                    )
                    try:
                        cost_price = bom_id.cost_price
                    except Exception as e:
                        _logger.exception(
                            "Failed to get cost price for [%s] %s\n %s",
                            reference.value, reference.product_id.name, e
                        )

            ref_price = False
            ref_prices = RefPrice.search(
                [('reference_id', '=', reference.id)], limit=1
            )
            if ref_prices:
                ref_price = ref_prices[0]

            if not ref_price or (round(ref_price.value, 2) != round(cost_price, 2)):
                #abs(ref_price.value - cost_price) > 0.1
                data = {
                    'reference_id': reference.id,
                    'value': cost_price,
                }
                RefPrice.create(data)
            else:
                _logger.info(
                    'Price did not change for [%s] %s', reference.value,
                    reference.product_id.name
                )

        self.generate_material_cost_report()

    @api.multi
    def generate_material_cost_report(
        self, date_ref1=False, date_ref2=False
    ):
        RefPrice = self.pool.get('ref.price')
        mail_message_obj = self.env['mail.mail'].sudo()

        if not self:
            self.search([]).generate_material_cost_report(())

        today = time.strftime('%Y-%m-%d')
        emailfrom = 'refmanager@dec-industrie.com'
        emails = ['decindustrie@gmail.com']
        subject = _('Price surcharge alert')
        body = ('%s\n\n') % (self.env.cr.dbname)
        ref_content = []

        for reference in self.browse(ids):
            if reference.category_id.name in ['ADT']:
                continue
            ref1_ids = []
            ref2_ids = []
            if date_ref1:
                ref1_ids = RefPrice.search(
                    [
                        ('reference_id', '=', reference.id),
                        ('date', '<=', date_ref1)
                    ],
                    limit=1
                )
            if date_ref2:
                ref2_ids = RefPrice.search(
                    [
                        ('reference_id', '=', reference.id),
                        ('date', '<=', date_ref2)
                    ],
                    limit=1
                )

            if ref1_ids and ref2_ids:
                price_ids = ref2_ids + ref1_ids
            else:
                price_ids = RefPrice.search(
                    [('reference_id', '=', reference.id)], limit=2
                )

            if (len(price_ids) >= 2):
                prices = RefPrice.browse(price_ids)
                if (round(prices[0].value, 2) > round(prices[1].value, 2)) and (
                    (date_ref1 or date_ref2) or (prices[0].date == today)
                ):
                    assert (prices[0].id == price_ids[0])
                    ref_content.append(
                        {
                            'id': reference.id,
                            'reference': reference.value,
                            'product': reference.product_id.name,
                            'price0_date': prices[0].date,
                            'price0_value': prices[0].value,
                            'price1_date': prices[1].date,
                            'price1_value': prices[1].value,
                            'diff': prices[0].value - prices[1].value
                        }
                    )

        ref_content = sorted(ref_content, key=lambda k: k['diff'], reverse=True)
        for content in ref_content:
            body += ('[%s] %s - %d\n') % (
                content['reference'], content['product'], content['id']
            )
            body += ('%s:   %.2f\n'
                    ) % (content['price1_date'], content['price1_value'])
            body += ('%s:   %.2f (+%.2f)\n') % (
                content['price0_date'], content['price0_value'],
                content['price0_value'] - content['price1_value']
            )
            body += '\n'

        if ref_content:
            mail_message_obj.create(
                {
                    #'email_from': emailfrom,
                    'email_to': emails,
                    'subject': subject,
                    'body_html': body
                }
            )
