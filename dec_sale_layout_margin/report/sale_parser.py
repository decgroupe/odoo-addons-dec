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
        order_lines = []
        product_obj = self.pool.get('product.product')
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        ids = purchase_order_line_obj.search(self.cr, self.uid, [('order_id', '=', order.id)])
        for id in range(0, len(ids)):
            order = purchase_order_line_obj.browse(self.cr, self.uid, ids[id], self.context.copy())
            order_lines.append(order)

        for line in order_lines:
            
            for res in result:
                if (res.product_id.id == line.product_id.id) and (res.product_uom.id == line.product_uom.id) and (res.price_unit == line.price_unit) and (res.notes == line.notes):
                    res.product_qty += line.product_qty
                    res.price_subtotal += line.price_subtotal
                    break
            else:
                partner_data = product_obj._get_partner_code_name(self.cr, self.uid, [], line.product_id, order.partner_id.id, context=self.context)
                
                line.supplier_code = partner_data['code']
                line.supplier_name = partner_data['name'] 
                line.has_notes = (line.notes != False)
                
                result.append(line)
            
        return result
