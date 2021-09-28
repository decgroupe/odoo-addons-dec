# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.misc import formatLang
from odoo.addons.tools_miscellaneous.tools.bench import Bench

from .ref_reference_line import AUTO_INC_CHAR

_logger = logging.getLogger(__name__)


class RefReference(models.Model):
    """ Description """

    _name = 'ref.reference'
    _description = 'Reference'
    _rec_name = 'value'
    _order = 'value'

    active = fields.Boolean(
        'Active',
        default=True,
        help="If unchecked, it will allow you to hide the reference "
        "without removing it.",
    )
    category_id = fields.Many2one(
        'ref.category',
        'Category',
        required=True,
    )
    # TODO: Step 1 : Rename to product_tmpl_id
    product_id = fields.Many2one(
        'product.template',
        'Product Template',
        required=True,
        copy=False,
    )
    # TODO: Step 2 : Rename to product_id
    product_variant_id = fields.Many2one(
        'product.product',
        'Product',
        copy=False,
        compute='_compute_product_variant_id',
        inverse='_inverse_product_variant_id',
    )
    public_code = fields.Char(
        related='product_id.public_code',
        string='Public Code',
        readonly=False,
    )
    name = fields.Char(
        related='product_id.name',
        string='Name',
        readonly=False,
    )
    state = fields.Selection(
        related='product_id.state',
        string='Status',
        readonly=False,
        default='quotation',
        store=True,
    )
    description = fields.Text(
        related='product_id.description',
        string='Internal Notes',
        readonly=False,
    )
    current_version = fields.Integer(
        'Current version',
        default=1,
        required=True,
        copy=False,
    )
    value = fields.Char(
        'Value',
        required=True,
        copy=False,
    )
    searchvalue = fields.Char(
        'Search value',
        required=True,
        copy=False,
    )
    datetime = fields.Datetime(
        'Create date',
        required=True,
        copy=False,
        default=fields.Datetime.now,
    )
    folder_count = fields.Integer(
        'Product folder item count',
        copy=False,
    )
    folder_error = fields.Integer(
        'Product folder error count',
        copy=False,
    )
    folder_warning = fields.Integer(
        'Product folder warning count',
        copy=False,
    )
    folder_task = fields.Integer(
        'Product folder task count',
        copy=False,
    )
    picturepath = fields.Char(
        'Path to picture',
        copy=False,
    )

    reference_line_ids = fields.One2many(
        'ref.reference.line',
        'reference_id',
        string='Lines',
    )
    version_ids = fields.One2many(
        'ref.version',
        'reference_id',
        string='Versions',
        copy=False,
    )

    _sql_constraints = [
        ('value_uniq', 'unique(value)', 'Reference value must be unique !'),
    ]

    def _prepare_product_vals(self, ref_vals):
        category_id = ref_vals.get('category_id')
        if category_id:
            product_categ_id = self.env['ref.category'].browse(category_id)\
                .product_category_id.id
        else:
            product_categ_id = False
        return {
            'name': ref_vals.get('name'),
            'default_code': ref_vals.get('value', '').replace(' ', ''),
            'mrp_production_request': True,
            'categ_id': product_categ_id,
            'sale_ok': True,
            'purchase_ok': False,
            'type': 'product',
            'state': ref_vals.get('state'),
            'procure_method': 'make_to_order',
            'supply_method': 'produce',
            'list_price': 0.0,
            'standard_price': 0.0,
            'sale_delay': 60,
            'produce_delay': 30,
        }

    @api.model
    def create(self, vals):
        if not vals.get('state'):
            vals['state'] = 'quotation'
        product_variant_id = vals.get('product_variant_id')
        if not product_variant_id:
            product_vals = self._prepare_product_vals(vals)
            product = self.env['product.product'].create(product_vals)
            vals['product_variant_id'] = product.id
        else:
            product = self.env['product.product'].browse(product_variant_id)
            product.mrp_production_request = True
        # Retrieve product template for variant
        if vals.get('product_id'):
            product_tmpl_id = self.env['product.template'].browse(
                vals.get('product_id')
            )
        elif vals.get('product_variant_id'):
            product_variant_id = vals.get('product_variant_id')
            product_tmpl_id = self.env['product.product'].browse(
                product_variant_id
            ).product_tmpl_id
        else:
            product_tmpl_id = False
        # Set product template since it is a required field
        if product_tmpl_id:
            vals['product_id'] = product_tmpl_id.id
        if not vals.get('version_ids'):
            author_id = self.env.context.get('author_id') or self.env.user.id
            vals['version_ids'] = [
                (
                    0, 0, {
                        'name': _('Initial Version'),
                        'version': 1,
                        'author_id': author_id,
                        'datetime': vals.get('datetime')
                    }
                )
            ]
        reference = super().create(vals)
        return reference

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'active' in vals:
            self.mapped('product_id').write({'active': vals.get('active')})
        return res

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % (self.name)
        reference_id = super().copy(default)
        return reference_id

    @api.depends('product_id')
    def _compute_product_variant_id(self):
        for rec in self:
            rec.product_variant_id = rec.product_id.product_variant_id

    def _inverse_product_variant_id(self):
        for rec in self:
            rec.product_id = rec.product_variant_id.product_tmpl_id

    @api.model
    def search_custom(self, keywords):
        res = []
        bench = Bench().start()
        for key in keywords[0]:
            if key and key[0] == '+':
                use_description = True
                key = key[1:]
            else:
                use_description = False

            if key:
                res_value = self.search([
                    ('searchvalue', 'ilike', key),
                ])
                res += res_value.ids
                res_category = self.search(
                    [
                        ('category_id.name', 'ilike', key),
                    ]
                )
                res += res_category.ids
                res_name = self.search([
                    ('product_id.name', 'ilike', key),
                ])
                res += res_name.ids
                res_public_code = self.search(
                    [
                        ('product_id.public_code', '=', key),
                    ]
                )
                res += res_public_code.ids

                if use_description:
                    res_description = self.search(
                        [
                            ('product_id.description', 'ilike', key),
                        ]
                    )
                    res += res_description.ids
                # A tag must be at least 2 characters
                if len(key) > 2:
                    res_tags = self.search(
                        [
                            ('product_id.tagging_ids.name', 'ilike', key),
                        ]
                    )
                    res += res_tags.ids

        _logger.info('Search elapsed time is %s', bench.stop().duration())
        return res

    @api.model
    def search_custom2(self, keywords):
        res = []
        value_domain = []
        category_domain = []
        name_domain = []
        public_code_domain = []
        description_domain = []
        tags_domain = []

        def add_to(domain, filter):
            if domain:
                domain[:] = expression.OR([domain, filter])
            else:
                domain[:] = filter
            return domain

        bench = Bench().start()
        for key in keywords[0]:
            if key and key[0] == '+':
                use_description = True
                key = key[1:]
            else:
                use_description = False

            if key:
                add_to(value_domain, [('searchvalue', 'ilike', key)])
                add_to(category_domain, [('category_id.name', 'ilike', key)])
                add_to(name_domain, [('product_id.name', 'ilike', key)])
                add_to(
                    public_code_domain, [('product_id.public_code', '=', key)]
                )
                if use_description:
                    add_to(
                        description_domain,
                        [('product_id.description', 'ilike', key)]
                    )
                # A tag must be at least 2 characters
                if len(key) > 2:
                    add_to(
                        tags_domain,
                        [('product_id.tagging_ids.name', 'ilike', key)]
                    )

        res_value = self.search(value_domain)
        res += res_value.ids
        res_category = self.search(category_domain)
        res += res_category.ids
        res_name = self.search(name_domain)
        res += res_name.ids
        res_public_code = self.search(public_code_domain)
        res += res_public_code.ids
        if description_domain:
            res_description = self.search(description_domain)
            res += res_description.ids
        if tags_domain:
            res_tags = self.search(tags_domain)
            res += res_tags.ids

        _logger.info('Search elapsed time is %s', bench.stop().duration())
        return res

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.ensure_one()
        vals = {}
        line_ids = []
        self.reference_line_ids = [(5, )]
        for line in self.category_id.category_line_ids:
            reference_line = (
                0, 0, {
                    'sequence': line.sequence,
                    'property_id': line.property_id.id,
                }
            )
            line_ids.append(reference_line)
        vals['reference_line_ids'] = line_ids
        self.update(vals)

    @api.onchange('reference_line_ids')
    def onchange_reference_line_ids(self):
        self.ensure_one()
        if not self.category_id:
            return
        self._update_indice()
        ref = [self.category_id.code]
        for line in self.reference_line_ids:
            default_value = '-' * len(line.property_id.format)
            if line.property_fixed:
                current_value = line.attribute_id.code
            else:
                current_value = line.value
            if current_value:
                current_value = current_value.replace(AUTO_INC_CHAR, '')
            ref.append(current_value or default_value)
        self.value = ' '.join(ref)
        self.searchvalue = ''.join(ref)

    def _update_indice(self):
        for line in self.reference_line_ids:
            # FIXME: Add a new auto_inc boolean property
            if not line.property_fixed and line.property_id.name == 'Indice':
                last_max_value = self._find_last_max_value(
                    self.category_id, self.reference_line_ids, line.property_id
                )
                # Auto update only if AUTO_INC_CHAR still exists
                if not line.value or AUTO_INC_CHAR in line.value:
                    formatted_value = line.property_id.format_int(
                        last_max_value + 1
                    )
                    line.value = AUTO_INC_CHAR + formatted_value

    @api.model
    def _find_last_max_value(
        self, category_id, reference_line_ids, property_id
    ):
        """ Browse each `reference_line_ids` one by one and retrieve all
            references of the same `category_id` using the same property
            combination.

        Args:
            category_id ([ref.category]): [description]
            reference_line_ids ([ref.reference.line]): [description]
            property_id ([ref.property]): [description]

        Returns:
            int: maximum attribute value already set
        """
        reference_ids = self.env['ref.reference']
        md = []
        for line in reference_line_ids:
            if line.property_id != property_id:
                domain = [
                    ('reference_id.category_id', '=', category_id.id),
                    ('sequence', '=', line.sequence),
                    ('property_id', '=', line.property_id.id),
                ]
                if line.property_id.fixed:
                    domain += [('attribute_id', '=', line.attribute_id.id)]
                else:
                    domain += [('value', '=', line.value)]
                # if not reference_ids:
                #     domain = [
                #         ('reference_id.category_id', '=', category_id.id)
                #     ] + domain
                # else:
                #     domain = [
                #         ('reference_id', 'in', reference_ids.ids)
                #     ] + domain

                reference_mapping_ids = self.env['ref.reference.line'].search(
                    domain
                ).mapped('reference_id')
                if not reference_ids:
                    reference_ids = reference_mapping_ids
                else:
                    reference_ids &= reference_mapping_ids
                    # If no union match at this point, just stop our search
                    if not reference_ids:
                        break

        max_value = 0
        if reference_ids:
            line_ids = self.env['ref.reference.line'].search(
                [
                    ('reference_id', 'in', reference_ids.ids),
                    ('property_id', '=', property_id.id),
                ]
            )
            for line in line_ids:
                try:
                    value = int(line.value)
                except ValueError:
                    value = 0  # TryGet default value
                if value > max_value:
                    max_value = value
        return max_value
