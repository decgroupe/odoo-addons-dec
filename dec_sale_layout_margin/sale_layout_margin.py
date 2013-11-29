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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import time
import netsvc


import decimal_precision as dp
from tools.translate import _

def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

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
        res = False
        if default is None:
            default = {}
        default['layout_type'] = self.browse(cr, uid, id, context=context).layout_type
        res = super(sale_order_line, self).copy(cr, uid, id, default, context)
        return res
    
    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'procurement_id': False, 'procurement_ids': []})
        return super(sale_order_line, self).copy_data(cr, uid, id, default, context=context)

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        return result
    
    def product_id_change_ext(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, price_unit=0.0, purchase_price=0.0, discount=0.0, context=None):
        result = self.product_id_change(cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        
        product_obj = self.pool.get('product.product')
        produit = product_obj.browse(cr, uid, [product], context=context)[0]
        
        # Remove price unit from result
        if product and flag:
            if 'value' in result and 'price_unit' in result['value']:
                del result['value']['price_unit']
                res2 = self.onchange_price_unit(cr, uid, ids, price_unit, purchase_price, qty, discount, context)
                result['value'].update(res2['value'])
        
        if product and not flag:
            if produit.ciel_code:
                name = '[%s] %s' % (produit.ciel_code, produit.name) 
                result['value'].update({'name': name})
                
                if produit.default_code and len(produit.default_code) > 3 and (produit.product_tmpl_id.supply_method == 'produce'):
                    notes =  'Ref. interne: [%s]' % (produit.default_code)
                    if result['value'].has_key('notes'):
                        notes = notes + '\n' + result['value'].get('notes', '')  
                    result['value'].update({'notes': notes})
                    
        if product and not flag:
            if produit.state == 'obsolete':
                warning = {}
                warning['title'] = _('Obsolete product!'), 
                warning['message'] = _('Obsolete product\n (This product must not be sold anymore.)\n\n %s') % (produit.comments or '')
                result['warning'] = warning
                
            elif produit.state == 'review':
                warning = {}
                warning['title'] = _('Review needed!'),
                warning['message'] = _('This product need to be reviewed:\n\n - %s \n\n - Please contact "%s"') % (produit.comments or _('No comments'), produit.product_manager and produit.product_manager.name or _('No manager for this product') )
                result['warning'] = warning
        
        if not pricelist:
            return result
        
        frm_cur = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        to_cur = self.pool.get('product.pricelist').browse(cr, uid, [pricelist])[0].currency_id.id
        
        if product: 
            purchase_price = produit.standard_price          
            if produit.seller_id:
                pricelist = produit.seller_id.property_product_pricelist_purchase
                if pricelist:
                    pricelist_pool = self.pool.get('product.pricelist')
                    purchase_price = pricelist_pool.price_get(cr,uid,[pricelist.id], produit.id, qty, produit.seller_id.id, {
                            'uom': uom,
                            'date': time.strftime('%Y-%m-%d'),
                            })[pricelist.id]
            
            price = self.pool.get('res.currency').compute(cr, uid, frm_cur, to_cur, purchase_price, round=False)
            result['value'].update({'purchase_price': price})
        return result
    
    ## Override default one
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, context=None):
        if context is None:
            context = {}
        lang = lang or context.get('lang',False)
        res = self.product_id_change_ext(cursor, user, ids, pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order, context=context)
        if 'product_uom' in res['value']:
            del res['value']['product_uom']
        if not uom:
            res['value']['price_unit'] = 0.0
        return res


    def uos_change(self, cr, uid, ids, product_uos, product_uos_qty=0, product_id=None):
        return {'value': {}} 
    
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
    
    def _get_sequence(self, cr, uid, context=None):
        if context is None:
            context = {}
            
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
        'order_id': fields.many2one('sale.order', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=False, states={'draft':[('readonly',False)]}),
        'layout_type': fields.selection([
                ('article', 'Product'),
                ('title', 'Title'),
                ('text', 'Note'),
                ('subtotal', 'Sub Total'),
                ('line', 'Separator Line'),
                ('break', 'Page Break'),]
            ,'Line Type', select=True, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'sequence': fields.integer('Line Sequence', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute= dp.get_precision('Product UoS')),
        'product_uom': fields.many2one('product.uom', 'Product UoM', readonly=True, states={'draft': [('readonly', False)]}),
        'procurement_ids': fields.one2many('procurement.order', 'sale_line_id', 'Procurements', readonly=True),
        # Override the field to call the overridden _amount_line function
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Sale Price')),
        'margin': fields.function(_product_margin, string='Margin', store = True),  
        'margin_percent': fields.float('Margin (%)', digits=(16,2)), # taux_marge = marge_commerciale/cout_achat_HT * 100
        'markup_percent': fields.float('Markup (%)', digits=(16,2)), # taux_marque = marge_commerciale/prix_vente_HT * 100
        'purchase_price': fields.float('Cost Price', digits_compute=dp.get_precision('Purchase Price')),
        
        # Changed by YP
        'product_id': fields.many2one('product.product', 'Product', domain=[], change_default=True, states={'draft': [('readonly', False)]}),
        'price_discount': fields.function(_discount_price, string='Unit Price (discount)', digits_compute= dp.get_precision('Sale Price')),
        
        'report_hide_line': fields.boolean('Hide Line', help="This allows the seller to hide the entire printed line"),
        'report_hide_uom': fields.boolean('Hide Uom', help="This allows the seller to hide units on the printed line"),

    }

    _defaults = {
        'layout_type': 'article',
        'purchase_price': 0.0,
        'sequence': _get_sequence,
    }

    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    def button_fix(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'procurement_id': False, 'procurement_ids': []})
        return res and self.button_done(cr, uid, ids, context=context)

    def compute_margin(self, price_unit, purchase_price, product_uos_qty, discount):
        result = (price_unit*product_uos_qty*(100.0-discount)/100.0) -(purchase_price*product_uos_qty)
        return round(result, 2)
        
    
    def onchange_price_unit(self, cr, uid, ids, price_unit, purchase_price, product_uos_qty, discount, context=None):
        if context is None:
            context = {}
            
        value = {'price_unit': price_unit}
            
        new_margin = self.compute_margin(price_unit, purchase_price, product_uos_qty, discount)   
        if (purchase_price > 0) and (product_uos_qty>0) and (price_unit>0):
            new_margin_percent = new_margin/float(product_uos_qty) * 100 / float(purchase_price) 
            new_markup_percent = new_margin/float(product_uos_qty) * 100 / float(price_unit - (price_unit*discount/100.0))  
        else:
            new_margin_percent = 0
            new_markup_percent = 0
            
        value.update({'margin': new_margin, 'margin_percent': new_margin_percent})
        value.update({'markup_percent': new_markup_percent})
        value.update({'price_subtotal': product_uos_qty * price_unit * (1 - (discount or 0.0) / 100.0)})
        return {'value': value}
    
    def onchange_margin_percent(self, cr, uid, ids, margin_percent, price_unit, purchase_price, product_uos_qty, discount, context=None):   
        value = {}
        return {'value': value}
        """
        print 'onchange_margin_percent'
        if context is None:
            context = {}
            
        new_price_unit = purchase_price / float(1-discount/100.0) * float(1+margin_percent/100.0) 
      
        context.update({'ignore_margin_update': True});
        return self.onchange_price_unit(cr, uid, ids, new_price_unit, purchase_price, product_uos_qty, discount, context)
        """
    
    def onchange_markup_percent(self, cr, uid, ids, markup_percent, price_unit, purchase_price, product_uos_qty, discount, context=None): 
        if context is None:
            context = {}
                  
        value = {}
        
        if purchase_price > 0:
            if markup_percent < 100: 
                new_price_unit = purchase_price / float(1-discount/100.0) / float(1-markup_percent/100.0) 
                new_price_unit = rounding(new_price_unit, 0.01)
            else:
                new_price_unit = 0
                
            value.update({'price_unit': new_price_unit})
        else:
            value.update({'markup_percent': 0})
            
        return {'value': value}
    
    def onchange_purchase_price(self, cr, uid, ids, price_unit, purchase_price, product_uos_qty, discount, context=None):
        if context is None:
            context = {}
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
    

    def write(self, cr, uid, ids, vals, context=None):

        locked_fields = set(['user_id','date_order','abstract_line_ids'])           
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.state == 'draft':
                # Check if someone is trying to unlock a quotation
                if vals.has_key('locked') and vals['locked'] <> sale.locked :
                    allow_lock_change = (uid == sale.user_id.id)
                    if allow_lock_change:
                        pass
                    else:
                        raise osv.except_osv(_('Operation forbidden'), _('Only %s is able to lock/unlock this object') % (sale.user_id.name))
                
                # Check if someone is trying to modify a locked quotation
                if not vals.has_key('locked') and sale.locked and locked_fields.intersection(vals): 
                    raise osv.except_osv(_('Operation forbidden'), _('%s is currently locked, you are not allowed to make changes') % (sale.name))
      
                
        if vals.get('partner_shipping_id', False): 
            # Shipping address change propagated to all attached picking
            picking_obj = self.pool.get('stock.picking')
            picking_ids = [x['picking_ids'] for x in self.read(cr, uid, ids, ['picking_ids'])]
            # Make a flatten list ie: [[1,2],[3]] -> [1,2,3]
            picking_ids = [item for sublist in picking_ids for item in sublist]
            picking_obj.write(cr, uid, picking_ids, {'address_id': vals['partner_shipping_id']}, context=context)
            
                
        return super(sale_order, self).write(cr, uid, ids, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        
        so = self.browse(cr, uid, id, context=context)  
        origin = so.origin
        if origin:
            origin = ('%s:%s') % (so.name, origin)
        else:
            origin = so.name
        
        default.update({
            'order_line': False, # all data is duplicated from abstract_line_ids
            'date_order': fields.date.context_today(self,cr,uid,context=context),
            'origin': origin,
            'locked': False,
        })
        res = super(sale_order, self).copy(cr, uid, id, default, context)
        return res
    

    # Override default
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """Create the required procurements to supply sale order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sale order's requested location.

        If ``picking_id`` is provided, the stock moves will be added to it, otherwise
        a standard outgoing picking will be created to wrap the stock moves, as returned
        by :meth:`~._prepare_order_picking`.

        Modules that wish to customize the procurements or partition the stock moves over
        multiple stock pickings may override this method and call ``super()`` with
        different subsets of ``order_lines`` and/or preset ``picking_id`` values.

        :param browse_record order: sale order to which the order lines belong
        :param list(browse_record) order_lines: sale order line records to procure
        :param int picking_id: optional ID of a stock picking to which the created stock moves
                               will be added. A new picking will be created if ommitted.
        :return: True
        """
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []
        
        def create_procurement_move(line, move_data):
            if move_data:
                move_id = move_obj.create(cr, uid, move_data)
            else:
                move_id = False
                
            proc_data = self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context)
            if move_data:
                proc_data['product_qty'] = move_data['product_qty']
            
            proc_id = procurement_obj.create(cr, uid, proc_data)
            proc_ids.append(proc_id)
            line.write({'procurement_id': proc_id})
            line.write({'procurement_ids': [(4, proc_id)]})
            
            self.ship_recreate(cr, uid, order, line, move_id, proc_id)

        for line in order_lines:
            if line.state == 'done':
                continue

            date_planned = self._get_date_planned(cr, uid, order, line, order.date_confirm, context=context) #https://code.launchpad.net/~openerp-dev/openobject-addons/6.1-opw-587363-ado

            # Create procurement for new lines but also for existing one where their procurement has been canceled
            if line.product_id:
                
                if line.state == 'confirmed':
                    # Do not recreate currently running procurement
                    if line.procurement_id and line.procurement_id.state in ('confirmed', 'running', 'ready', 'done', 'waiting'):
                        continue
                elif line.state == 'exception':
                    # Reset line state to confirmed state
                    self.pool.get('sale.order.line').button_confirm(cr, uid, [line.id]) 
                    # Cancel existing move if the canceled procurement exists 
                    if line.procurement_id and line.procurement_id.state == 'cancel'\
                    and line.procurement_id.move_id and line.procurement_id.move_id.state not in ('done', 'cancel'):
                        move_obj.action_cancel(cr, uid, [line.procurement_id.move_id.id])
                
                if line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                        
                    move_data = self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context) 
                        
                    # Specific for DEC Industrie: Split 1 procurement of Qty=n into n x procurements of Qty=1
                    if line.product_id.procure_method=='make_to_order' and line.product_id.supply_method=='produce':
                        qty = int(line.product_uom_qty)
                        assert line.product_uom_qty / qty == 1 # assert 1.0 = 1

                        for i in range(1, qty+1):
                            alt_data = move_data.copy() 
                            alt_data['product_qty'] = 1.0 
                            create_procurement_move(line, alt_data)
                            
                    else:
                        create_procurement_move(line, move_data)                       
                        
                else:
                    # a service has no stock move
                    create_procurement_move(line, False)  

        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True

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
    
    # Override default
    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        dt_startdate = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        date_planned = dt_startdate +  relativedelta(list(rrule(DAILY, count=1+(line.delay or 0.0), byweekday=(MO,TU,WE,TH,FR)))[-1], dt_startdate)
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        result = date_planned
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
    
    

    def _picked_in_rate(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}

        move_obj = self.pool.get('stock.move') 
        for order in self.browse(cr, uid, ids, context=context):
            ready_count = 0
            total_count = 0
            
            picking_ids = []
            for picking in order.picking_ids:
                if picking.state not in ['cancel']: 
                    picking_ids.append(picking.id)
            
            move_ids = move_obj.search(cr, uid, [('picking_id', 'in', picking_ids)])
            move_ids = move_obj.browse(cr, uid, move_ids, context=context)
            for move in move_ids: 
                total_count += 1
                if move.state in ('assigned','done','cancel'):
                    ready_count += 1
                      
            if total_count > 0: 
                res[order.id] = float(ready_count)/float(total_count) * 100
            else:   
                res[order.id] = order.picked_rate 

                
        return res

    _inherit = "sale.order"
    _columns = {
        'partner_shipping_id': fields.many2one('res.partner.address', 'Shipping Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'manual':[('readonly',False)]}, help="Shipping address for current sales order."),
        'abstract_line_ids': fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'order_line': one2many_mod2('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'margin': fields.function(_product_margin, string='Margin', help="It gives profitability by calculating the difference between the Unit Price and Cost Price.", store={}),
        'summary': fields.char('Summary', size=64),
        'validity': fields.integer('Validity period', readonly=True, states={'draft': [('readonly', False)]}, help="Validity delay in day(s)"),
        'warranty': fields.integer('Warranty period', readonly=True, states={'draft': [('readonly', False)]}, help="Warranty delay in year(s)"),
        'validity_date': fields.function(_get_validity_date, store=True, type='date', string='Validity Date', help="Date of validity"),
        'partner_delivery_id': fields.related('partner_shipping_id', 'partner_id', type='many2one', relation='res.partner', string='Alloted'),
        'partner_delivery_city_id': fields.related('partner_shipping_id', 'city_id', type='many2one', relation='city.city', string='City'),
        'picked_in_rate': fields.function(_picked_in_rate, string='Received', type='float'),
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_rel', 'order_id', 'invoice_id', 'Invoices', readonly=False, help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example)."),
        'picking_ids': fields.one2many('stock.picking', 'sale_id', 'Related Picking', readonly=False, help="This is a list of picking that has been generated for this sales order."),
        'locked': fields.boolean('Locked', help="This allows the seller to prevent changes by other users.", readonly=True, states={'draft': [('readonly', False)]}),
    }
    _defaults = {
        'validity': 30,
        'warranty': 1,
    }
    
    # Override default
    def action_ship_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            self._create_pickings_and_procurements(cr, uid, order, order.order_line, None, context=context)
        return True
    
    def action_wait(self, cr, uid, ids, context=None):
        
        product_pool = self.pool.get('product.product')
        bom_pool = self.pool.get('mrp.bom')
            
        msg = ''        
        for sale in self.browse(cr, uid, ids):              
            for line in sale.order_line:
                if line.product_id and (line.type == 'make_to_order') and (line.product_id.product_tmpl_id.type == 'product') and (line.product_id.product_tmpl_id.supply_method == 'produce'):
                    err1 = ''
                    err2 = ''
                    if not line.product_id.state in ['draft', 'review', 'sellable']:   
                        err1 = _('Cannot sell this product (state is quotation, review or obsolete)')   
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
    
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        picking_ids = []
        for sale in self.browse(cr, uid, ids, context=context):
            for pick in sale.picking_ids:
                if pick.state not in ('draft', 'cancel'):
                    picking_ids.append(pick.id)
                    
        if picking_ids:
            picking_obj.action_cancel(cr, uid, picking_ids, context=context)
                    
        return super(sale_order, self).action_cancel(cr, uid, ids, context=context)
    

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        vals = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=context)

        if move_line.sale_line_id:
            vals['sequence'] = move_line.sale_line_id.sequence

        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
