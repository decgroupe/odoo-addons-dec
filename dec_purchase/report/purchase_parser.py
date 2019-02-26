##############################################################################
#
#
##############################################################################

from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'purchase_order_lines': self.purchase_order_lines,
            'hello_world':self.hello_world,
        })
        self.context = context

    def hello_world(self, name):
        return "Hello, %s!" % name

    def purchase_order_lines(self, order):
        result = []
        product_obj = self.pool.get('product.product')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        order_lines_ids = purchase_order_line_obj.search(self.cr, self.uid, [('order_id', '=', order.id)])        
        order_lines = purchase_order_line_obj.browse(self.cr, self.uid, order_lines_ids, self.context.copy())   
        total_amounts = self.datas.has_key('form') and self.datas['form'].has_key('total_amounts') and self.datas['form']['total_amounts']  
        pack_print = self.datas.has_key('form') and self.datas['form'].get('pack_print', 'default')   
        pack_hide_prices = self.datas.has_key('form') and self.datas['form'].get('pack_hide_prices', False)   
        

        for line in order_lines:
            
            if line.pack_parent_line_id:
                if (pack_print == 'default' and not line.pack_parent_line_id.pack_print) or (pack_print == 'hide'):
                    continue
                elif pack_print == 'show':
                    pass
                
            for res in result:
                if total_amounts and (res.product_id.id == line.product_id.id) and (res.product_uom.id == line.product_uom.id) and (res.price_unit == line.price_unit) and (res.notes == line.notes):
                    res.product_qty += line.product_qty
                    res.price_subtotal += line.price_subtotal
                    break
            else:
                partner_data = product_obj._get_partner_code_name(self.cr, self.uid, [], line.product_id, order.partner_id.id, context=self.context)
                
                if line.pack_parent_line_id:
                    line.hide_price = pack_hide_prices
                else:
                    line.hide_price = False
                
                line.supplier_code = partner_data['code']
                line.supplier_name = partner_data['name'] 
                line.has_notes = (line.notes != False)
                
                result.append(line)
            
        return result
