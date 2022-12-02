# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.tools.progressbar import progressbar as pb

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Override digit field to increase precision and track changes
    standard_price = fields.Float(
        digits='Purchase Price', tracking=True
    )
    # Override to track changes
    list_price = fields.Float(tracking=True)

    standard_price_po_uom = fields.Float(
        'Cost (Purchase UoM)',
        compute='_compute_standard_price_po_uom',
        inverse='_set_standard_price_po_uom',
        digits='Product Price',
        groups="base.group_user",
        help='Same field than standard_price but expressed in "Purchase Unit '
        'of Measure".',
    )
    # Used only to hide standard_price_po_uom field from view if not needed
    same_uom = fields.Boolean(
        compute='_compute_same_uom',
        store=True,
        compute_sudo=True,
        help='Are "Default Unit of Measure" and "Purchase Unit of Measure" '
        'identical ?',
    )
    default_purchase_price = fields.Monetary(
        compute='_compute_default_purchase_price',
        string='Purchase Price (Default UoM)',
        digits='Purchase Price',
        help='Purchase price based on default seller pricelist computed with '
        '"Default Unit of Measure"',
    )
    default_purchase_price_graph = fields.Char(
        compute='_compute_default_purchase_price',
        string='Purchase Price Graph (Default UoM)',
    )
    default_purchase_price_po_uom = fields.Monetary(
        compute='_compute_default_purchase_price',
        string='Purchase Price',
        digits='Purchase Price',
        help='Purchase price based on default seller pricelist computed with '
        '"Purchase Unit of Measure"',
    )
    default_purchase_price_graph_po_uom = fields.Char(
        compute='_compute_default_purchase_price',
        string='Purchase Price Graph',
    )
    default_sell_price = fields.Monetary(
        compute='_compute_default_sell_price',
        string='Sell Price',
        digits='Product Price',
        help="Sell price based on default sell pricelist",
    )
    default_sell_price_graph = fields.Char(
        compute='_compute_default_sell_price',
        string='Sell Price Graph',
    )
    pricelist_bypass = fields.Boolean(
        'By-pass',
        help="A bypass action will create a pricelist item to overwrite "
        "pricelist computation",
    )
    pricelist_bypass_item = fields.Many2one(
        'product.pricelist.item',
        'Pricelist item',
    )
    market_place = fields.Boolean(
        'Market place',
        help="Tip to know if the product must be displayed on the market place",
    )
    price_write_date = fields.Datetime('Price write date')
    price_write_uid = fields.Many2one(
        'res.users',
        'Price last editor',
    )
    standard_price_write_date = fields.Datetime('Standard price write date')
    standard_price_write_uid = fields.Many2one(
        'res.users',
        'Standard price last editor',
    )

    @api.onchange('standard_price_po_uom')
    def onchange_standard_price_po_uom(self):
        self._set_standard_price_po_uom()

    @api.depends('standard_price', 'uom_id', 'uom_po_id')
    def _compute_standard_price_po_uom(self):
        # Check that uom_id is not False (possibility in editing mode)
        for product in self.filtered('uom_id'):
            price = product.uom_id._compute_price(
                product.standard_price,
                product.uom_po_id,
            )
            _logger.debug('New standard_price_po_uom = {}'.format(price))
            product.standard_price_po_uom = price

    def _set_standard_price_po_uom(self):
        # Check that uoms are not False (possibility in editing mode)
        for product in self.filtered('uom_po_id').filtered('uom_id'):
            price = product.uom_po_id._compute_price(
                product.standard_price_po_uom,
                product.uom_id,
            )
            _logger.debug('New standard_price = {}'.format(price))
            product.standard_price = price

    @api.depends('uom_id', 'uom_po_id')
    def _compute_same_uom(self):
        for product in self:
            product.same_uom = (product.uom_id.id == product.uom_po_id.id)

    @api.onchange('list_price', 'standard_price', 'uom_id', 'uom_po_id')
    def onchange_prices(self):
        self._compute_default_purchase_price()

    def get_purchase_price(self, seller_id=False, uom_id=False):
        """Use same logic from _compute_default_purchase_price without
            the history thing

        Args:
            seller_id (bool, optional): Partner to use to get purchase 
            pricelist. Use the seller_id from product if not set. Defaults
            to False.
            uom_id (bool, optional): Unit used to compute the price. Use the
            uom_id from product Defaults to False.

        Returns:
            float: Purchase price
        """
        self.ensure_one()
        res = 0
        if not seller_id:
            seller_id = self.seller_id
        if not uom_id:
            uom_id = self.uom_id
        if seller_id:
            pricelist = seller_id.property_product_pricelist_purchase
            if pricelist:
                res = pricelist.get_product_price(
                    self, 1, False, uom_id=uom_id.id
                )
        else:
            res = self.standard_price
        return res

    @api.depends(
        'seller_id',
        'standard_price',
        'uom_id',
        'uom_po_id',
    )
    def _compute_default_purchase_price(self):
        for p in pb(self):
            if isinstance(p.id, models.NewId):
                continue
            if p.seller_id:
                history = {}
                pricelist = p.seller_id.property_product_pricelist_purchase.\
                    with_context(history=history)
                if pricelist:
                    p.default_purchase_price = \
                        pricelist.get_product_price(
                            p, 1, False, uom_id=p.uom_id.id
                        )
                    graph = history[p.id]['graph']['header'] + \
                            history[p.id]['graph']['body']
                    p.default_purchase_price_graph = '\n'.join(graph)

                    history.clear()
                    p.default_purchase_price_po_uom = \
                        pricelist.get_product_price(
                            p, 1, False, uom_id=p.uom_po_id.id
                        )
                    graph = history[p.id]['graph']['header'] + \
                            history[p.id]['graph']['body']
                    p.default_purchase_price_graph_po_uom = '\n'.join(graph)
            else:
                p.default_purchase_price = p.standard_price
                p.default_purchase_price_graph = False
                p.default_purchase_price_po_uom = p.standard_price_po_uom
                p.default_purchase_price_graph_po_uom = False

    @api.depends(
        'company_id',
        'list_price',
        'standard_price',
        'uom_id',
    )
    def _compute_default_sell_price(self):
        for p in pb(self):
            if isinstance(p.id, models.NewId):
                continue
            if p.company_id and p.company_id.partner_id:
                history = {}
                pricelist = p.company_id.partner_id.\
                    property_product_pricelist.with_context(history=history)
                if pricelist:
                    p.default_sell_price = \
                        pricelist.get_product_price(
                            p, 1, False, uom_id=p.uom_id.id
                        )
                    graph = history[p.id]['graph']['header'] + \
                            history[p.id]['graph']['body']
                    p.default_sell_price_graph = '\n'.join(graph)
            else:
                p.default_sell_price = p.list_price
                p.default_sell_price_graph = False

    def update_bypass(self, state):
        Pricelist = self.env['product.pricelist']
        PricelistItem = self.env['product.pricelist.item']
        for product_tmpl_id in self:
            # Currently, we just assert that there is only one variant.
            product_id = product_tmpl_id.product_variant_id
            pricelists = Pricelist.search([('type', '=', 'sale')])
            pricelist_items = PricelistItem.search(
                [
                    ('pricelist_id', 'in', pricelists.ids),
                    '|',
                    ('product_tmpl_id', '=', product_tmpl_id.id),
                    ('product_id', '=', product_id.id),
                ]
            )

            if state:
                if not pricelist_items:
                    data = {
                        'sequence': 2,
                        'note': _('By-pass {}').format(product_tmpl_id.\
                            default_code),
                        'pricelist_id': pricelists.ids[0],
                        'product_tmpl_id': product_tmpl_id.id,
                        'product_id': product_id.id,
                        'compute_price': 'formula',
                        'applied_on': '1_product',
                        'base': 'list_price',
                        'company_id': product_tmpl_id.company_id.id,
                    }
                    product_tmpl_id.pricelist_bypass_item = PricelistItem.create(
                        data
                    )
            else:
                if len(pricelist_items) > 1:
                    raise UserError(
                        _(
                            'Too many pricelist items for this product!, only '
                            'one sale pricelist item must exist for this '
                            'product to disable by-pass functionality'
                        )
                    )
                elif pricelist_items:
                    pricelist_items.unlink()

    def write(self, vals):
        if 'list_price' in vals:
            vals['price_write_date'] = fields.Datetime.to_string(
                datetime.now()
            ),
            vals['price_write_uid'] = self.env.user.id
        if 'standard_price' in vals:
            vals['standard_price_write_date'] = fields.Datetime.to_string(
                datetime.now()
            ),
            vals['standard_price_write_uid'] = self.env.user.id
        if 'pricelist_bypass' in vals:
            self.update_bypass(state=vals['pricelist_bypass'])
        res = super().write(vals)
        return res

    def open_price_graph(self):
        self.ensure_one()
        # TODO: Open a wizard, first, to select the variant that will be used
        # to compute the graph.
        # Currently, we just assert that there is only one variant.
        action = self.product_variant_id.open_price_graph()
        return action

    @api.model
    def convert_openerp_to_odoo_prices(self):
        """
            With our OpenERP, instance, prices were set for purchase UoM
            but now, we are using the Odoo way, so all prices must be set
            for product Uom. This function is done to be called only once,
            and immediatly after the migration.
        """
        SUBJECT = 'Price Conversion'
        FIELDS = [
            'name', 'default_code', 'standard_price', 'list_price', 'uom_id',
            'uom_po_id'
        ]
        done_ids = []
        product_ids = self.search([('same_uom', '!=', True)])
        product_ids = self.env['product.product'].search(
            [('same_uom', '!=', True)]
        )
        notification_ids = self.env['mail.message'].search(
            [
                ('model', '=', self._name), ('res_id', 'in', product_ids.ids),
                ('message_type', '=', 'notification'),
                ('subject', '=', SUBJECT)
            ]
        )
        if notification_ids:
            done_ids = notification_ids.mapped('res_id')

        product_price_precision = self.env['decimal.precision'].precision_get(
            'Product Price'
        )
        purchase_price_precision = self.env['decimal.precision'].precision_get(
            'Purchase Price'
        )

        for product_id in product_ids:
            if product_id.id in done_ids:
                continue
            p = product_id.read(FIELDS)[0]
            uom_id = self.env['uom.uom'].browse(p['uom_id'][0])
            uom_po_id = self.env['uom.uom'].browse(p['uom_po_id'][0])
            _logger.info(
                '[%s]%s:  %.2f=1x%s  %.4f=1x%s', p['default_code'], p['name'],
                p['list_price'], uom_id.name, p['standard_price'],
                uom_po_id.name
            )
            ratio = uom_po_id.factor_inv * uom_id.factor_inv
            list_price = float_round(
                p['list_price'] / ratio,
                precision_digits=product_price_precision
            )
            standard_price = float_round(
                p['standard_price'] / ratio,
                precision_digits=purchase_price_precision
            )

            data = {}
            body = []
            # Prepare data that will update sell price (list_price)
            if float_compare(
                p['list_price'],
                list_price,
                precision_digits=product_price_precision
            ) != 0:
                data['list_price'] = list_price
                body.append(
                    _('Sell price set to {} (from {} for 1×{})').format(
                        list_price, p['list_price'], uom_po_id.name
                    )
                )
            # Prepare data that will update sell price (list_price)
            if float_compare(
                p['standard_price'],
                standard_price,
                precision_digits=purchase_price_precision
            ) != 0:
                data['standard_price'] = standard_price
                body.append(
                    _('Purchase price set to {} (from {} for 1×{})').format(
                        standard_price, p['standard_price'], uom_po_id.name
                    )
                )

            if body:
                body = '\n'.join(body)
                _logger.info(
                    'New prices are: {}, {}'.format(list_price, standard_price)
                )
                product_id.message_post(body=body, subject=SUBJECT)

            if data:
                product_id.write(data)
                self.env.cr.commit()
