##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
import time

import decimal_precision as dp
from tools.translate import _

class sale_order_line(osv.osv):
    
              
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        line_ids = []
        for id in ids:
            res[id] = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.layout_type == 'article':
                line_ids.append(line.id)
        if line_ids:
            res_article = super(sale_order_line, self)._amount_line(cr, uid, line_ids, field_name, arg, context)
            res.update(res_article)
        return res
              
    # same code than _amount_line but with quantity set to 1 or 0
    def _discount_price(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        
        res = {}
        line_ids = []
        for id in ids:
            res[id] = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            if line.layout_type == 'article':
                line_ids.append(line.id)
                
        for line in self.browse(cr, uid, line_ids, context=context):          
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            quantity = 1.0 if line.product_uom_qty > 0 else 0.0
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, quantity, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    def invoice_line_create(self, cr, uid, ids, context=None):
        new_ids = []
        list_seq = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.layout_type == 'article':
                new_ids.append(line.id)
                list_seq.append(line.sequence)
        invoice_line_ids = super(sale_order_line, self).invoice_line_create(cr, uid, new_ids, context)
        pool_inv_line = self.pool.get('account.invoice.line')
        seq = 0
        for obj_inv_line in pool_inv_line.browse(cr, uid, invoice_line_ids, context=context):
            pool_inv_line.write(cr, uid, [obj_inv_line.id], {'sequence': list_seq[seq]}, context=context)
            seq += 1
        return invoice_line_ids

    def onchange_sale_order_line_view(self, cr, uid, id, type, context={}, *args):
        temp = {}
        temp['value'] = {}
        if (not type):
            return {}
        if type != 'article':
            temp = {
                'value': {
                'product_id': False,
                'uos_id': False,
                'account_id': False,
                'price_unit': 0.0,
                'price_subtotal': 0.0,
                'quantity': 0,
                'discount': 0.0,
                'invoice_line_tax_id': False,
                'account_analytic_id': False,
                'product_uom_qty': 0.0,
                },
            }
            if type == 'line':
                temp['value']['name'] = ' '
            if type == 'break':
                temp['value']['name'] = ' '
            if type == 'subtotal':
                temp['value']['name'] = 'Sub Total'
            return temp
        return {}

    def create(self, cr, user, vals, context=None):
        #vals['purchase_price'] = 666
        if vals.has_key('layout_type'):
            if vals['layout_type'] == 'line':
                vals['name'] = ' '
            if vals['layout_type'] == 'break':
                vals['name'] = ' '
            if vals['layout_type'] != 'article':
                vals['product_uom_qty']= 0
        return super(sale_order_line, self).create(cr, user, vals, context)

    def write(self, cr, user, ids, vals, context=None):
        if vals.has_key('layout_type'):
            if vals['layout_type'] == 'line':
                vals['name'] = ' '
            if vals['layout_type'] == 'break':
                vals['name'] = ' '
        return super(sale_order_line, self).write(cr, user, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['layout_type'] = self.browse(cr, uid, id, context=context).layout_type
        return super(sale_order_line, self).copy(cr, uid, id, default, context)


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        
        if product and not flag:
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, product, context=context)
            if product_obj.ciel_code:
                name = '[%s] %s' % (product_obj.ciel_code, product_obj.name) 
                result['value'].update({'name': name})
                
                if product_obj.default_code:
                    notes =  'Ref. interne: [%s]' % (product_obj.default_code)
                    if result['value'].has_key('notes'):
                        notes = notes + '\n' + result['value'].get('notes', '')  
                    result['value'].update({'notes': notes})
        
        if not pricelist:
            return result
        frm_cur = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        to_cur = self.pool.get('product.pricelist').browse(cr, uid, [pricelist])[0].currency_id.id
        if product and not flag:
            purchase_price = self.pool.get('product.product.extended').browse(cr, uid, product).default_supplier_price
            price = self.pool.get('res.currency').compute(cr, uid, frm_cur, to_cur, purchase_price, round=False)
            result['value'].update({'purchase_price': price})
        return result

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.layout_type == 'article':
                purchase_price = line.purchase_price or 0.0
                line_margin = self.compute_margin(line.price_unit, purchase_price, line.product_uos_qty, line.discount) 
                res[line.id] = line_margin
#                if line.purchase_price:
#                    res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.purchase_price*line.product_uos_qty), 2)
#                else:
#                    res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.product_id.standard_price*line.product_uos_qty), 2)
        return res
    
    def _get_sequence(self, cr, uid, context={}):
        result = 0
        if context and 'order_id' in context:
            sale_orders = self.pool.get('sale.order').browse(cr, uid, context['order_id'])
            for abstract_line in sale_orders.abstract_line_ids:
                if abstract_line.sequence >= result:
                    result = abstract_line.sequence+1          
            
        return int(time.time())
    
    _order = "order_id, sequence asc"
    _description = "Sales Order line"
    _inherit = "sale.order.line"
    _columns = {
        'layout_type': fields.selection([
                ('article', 'Product'),
                ('title', 'Title'),
                ('text', 'Note'),
                ('subtotal', 'Sub Total'),
                ('line', 'Separator Line'),
                ('break', 'Page Break'),]
            ,'Line Type', select=True, required=True),
        'sequence': fields.integer('Line Sequence', select=True),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute= dp.get_precision('Product UoS')),
        'product_uom': fields.many2one('product.uom', 'Product UoM'),
        # Override the field to call the overridden _amount_line function
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),
        'margin': fields.function(_product_margin, string='Margin', store = True),  
        'margin_percent': fields.float('Margin (%)', digits=(16,2)), # taux_marge = marge_commerciale/cout_achat_HT * 100
        'markup_percent': fields.float('Markup (%)', digits=(16,2)), # taux_marque = marge_commerciale/prix_vente_HT * 100
        'purchase_price': fields.float('Cost Price', digits=(16,2)),
        
        # Changed by YP
        'product_id': fields.many2one('product.product', 'Product', domain=[], change_default=True),
        'price_discount': fields.function(_discount_price, string='Unit Price (discount)', digits_compute= dp.get_precision('Sale Price')),
        
        #'tax_id': fields.many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes', readonly=False, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'layout_type': 'article',
        'purchase_price': 0.0,
        'sequence': _get_sequence,
    }

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def compute_margin(self, price_unit, purchase_price, product_uos_qty, discount):
        result = (price_unit*product_uos_qty*(100.0-discount)/100.0) -(purchase_price*product_uos_qty)
        return round(result, 2)
        
    
    def onchange_price_unit(self, cr, uid, ids, price_unit, purchase_price, product_uos_qty, discount, context={}):
        value = {'price_unit': price_unit}
            
        new_margin = self.compute_margin(price_unit, purchase_price, product_uos_qty, discount)   
        if (purchase_price > 0) and (product_uos_qty>0) and (price_unit>0):
            new_margin_percent = new_margin/float(product_uos_qty) * 100 / float(purchase_price) 
            new_markup_percent = new_margin/float(product_uos_qty) * 100 / float(price_unit - (price_unit*discount/100.0))  
        else:
            new_margin_percent = 0
            new_markup_percent = 0
            
        if not context.get('ignore_margin_update', False):
            value.update({'margin': new_margin, 'margin_percent': new_margin_percent})
            
        if not context.get('ignore_markup_update', False):
            value.update({'markup_percent': new_markup_percent})

        return {'value': value}
    
    def onchange_margin_percent(self, cr, uid, ids, margin_percent, price_unit, purchase_price, product_uos_qty, discount, context={}):   
        new_price_unit = purchase_price / float(1-discount/100.0) * float(1+margin_percent/100.0) 
      
        context.update({'ignore_margin_update': True});
        return self.onchange_price_unit(cr, uid, ids, new_price_unit, purchase_price, product_uos_qty, discount, context)
    
    def onchange_markup_percent(self, cr, uid, ids, markup_percent, price_unit, purchase_price, product_uos_qty, discount, context={}):       
        if markup_percent < 100: 
            new_price_unit = purchase_price / float(1-discount/100.0) / float(1-markup_percent/100.0) 
        else:
            new_price_unit = 0
            
        context.update({'ignore_markup_update': True});
        result = self.onchange_price_unit(cr, uid, ids, new_price_unit, purchase_price, product_uos_qty, discount, context) 
        return result
    
    def onchange_purchase_price(self, cr, uid, ids, price_unit, purchase_price, product_uos_qty, discount, context={}):
        return self.onchange_price_unit(cr, uid, ids, price_unit, purchase_price, product_uos_qty, discount, context)
        
    
sale_order_line()

class one2many_mod2(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not values:
            values = {}
        res = {}
        for id in ids:
            res[id] = []
        ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id, 'in', ids), ('layout_type', '=', 'article')], limit=self._limit)
        for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
            res[r[self._fields_id]].append( r['id'] )
        return res


class sale_order(osv.osv):
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['order_line'] = False
        return super(sale_order, self).copy(cr, uid, id, default, context)

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 0.0
            for line in sale.order_line:
                result[sale.id] += line.margin or 0.0
        return result

    def _get_order(self, cr, uid, ids, context=None):
        parent_get_order = super(sale_order, self.pool.get('sale.order'))._get_order.im_func
        return parent_get_order(self, cr, uid, ids, context=context)
    
    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        result = super(sale_order, self)._get_date_planned(cr, uid, order, line, start_date, context=context)
        if order.requested_date and (order.requested_date > result):
            result = order.requested_date        
        return result
    
    def _get_validity_date(self, cr, uid, ids, name, arg, context=None):
        result = {}
        dates_list = []
        for order in self.browse(cr, uid, ids, context=context):
            dates_list = []
            dt = datetime.strptime(order.date_order, '%Y-%m-%d') + relativedelta(days=order.validity or 0.0)
            result[order.id] = dt.strftime('%Y-%m-%d')
                
        return result
    
    
    def _get_partner_shipping(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
            
        for order in self.browse(cr, uid, ids, context=context):    
            if order.partner_shipping_id and order.partner_shipping_id.partner_id:
                res[order.id] = order.partner_shipping_id.partner_id.name
            else:
                res[order.id] = False;

        return res
    
    def _get_partner_shipping_city(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
            
        for order in self.browse(cr, uid, ids, context=context):    
            if order.partner_shipping_id:
                res[order.id] = order.partner_shipping_id.city
            else:
                res[order.id] = False;

        return res


    _inherit = "sale.order"
    _columns = {
        'abstract_line_ids': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'order_line': one2many_mod2('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
#        'margin': fields.function(_product_margin, string='Margin', help="It gives profitability by calculating the difference between the Unit Price and Cost Price.", store={
#                'sale.order.line': (_get_order, [], 20),
#                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 20),
#                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['abstract_line_ids'], 20),
#                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['summary'], 10),
#                }),
        'margin': fields.function(_product_margin, string='Margin', help="It gives profitability by calculating the difference between the Unit Price and Cost Price.", store={}),
        'summary': fields.char('Summary', size=64),
        'validity': fields.integer('Validity period', readonly=True, states={'draft': [('readonly', False)]}, help="Validity delay in day(s)"),
        'warranty': fields.integer('Warranty period', readonly=True, states={'draft': [('readonly', False)]}, help="Warranty delay in year(s)"),
        'validity_date': fields.function(_get_validity_date, store=True, type='date', string='Validity Date', help="Date of validity"),
#        'partner_shipping': fields.function(_get_partner_shipping, store=False, type='char', string="Partner"),
        'partner_delivery_id': fields.related('partner_shipping_id', 'partner_id', type='many2one', relation='res.partner', string='Alloted'),
        'partner_delivery_city_id': fields.related('partner_shipping_id', 'city_id', type='many2one', relation='city.city', string='City'),
#        'partner_delivery_city': fields.related('partner_shipping_id', 'city', type='char', string='City'),
    }
    _defaults = {
        'validity': 30,
        'warranty': 1,
    }
    
    def action_wait(self, cr, uid, ids, context=None):
        
        product_pool = self.pool.get('product.product')
        bom_pool = self.pool.get('mrp.bom')
            
        msg = ''        
        for sale in self.browse(cr, uid, ids):              
            for line in sale.order_line:
                if line.product_id and (line.type == 'make_to_order') and (line.product_id.product_tmpl_id.type == 'product') and (line.product_id.product_tmpl_id.supply_method == 'produce'):
                    err1 = ''
                    err2 = ''
                    if not line.product_id.state in ['draft', 'sellable']:   
                        err1 = _('Cannot sell this product (state is quotation or obsolete)')   
                    if not line.product_id.bom_ids:            
                        err2 = _('Missing BoM')
                    else:
                        mrp_pool = self.pool.get('mrp.bom')
                        for bom_id in line.product_id.bom_ids:  
                            if (bom_id == False) and not bom_id.bom_lines: # Check for empty BoM, only first level BoM (no parent)
                                err2 = _('Empty BoM (%s) %d') % (bom_id.name, bom_id.sequence)
                                                  
                    if err1 <> '' or err2 <> '':
                        msg = msg + '[%s]\n' % (line.product_id.default_code or line.product_id.name)   
                        if err1 <> '': 
                            msg = msg + ' -%s\n' % (err1)   
                        if err2 <> '': 
                            msg = msg + ' -%s\n' % (err2)  
                            
                        msg = msg + '\n' 
                        
        #msg = msg + 'YP'
                        
        if msg <> '':
            raise osv.except_osv(_('Error !'), msg)
            
        return super(sale_order, self).action_wait(cr, uid, ids, context);

sale_order()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        vals = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=context)

        if move_line.sale_line_id:
            vals['sequence'] = move_line.sale_line_id.sequence

        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
