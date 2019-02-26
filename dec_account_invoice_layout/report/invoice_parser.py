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
            'current_subtotal': self._current_subtotal,
            'get_bank_from_wizard':self.get_bank_from_wizard,
            'tax_summary':self.tax_summary,
        })
        self.context = context

    def _current_subtotal(self, order, current_line):
        sum = 0
        for line in order.abstract_line_ids:
            sum = sum + line.price_subtotal
            if line == current_line:
                return sum
            elif line.layout_type == 'subtotal':
                sum = 0 
            
        return 0
    
    def get_bank_from_wizard(self):
        result = False
        partner_bank_tuple = self.datas.has_key('form') and self.datas['form'].get('partner_bank_id', result)   
        if partner_bank_tuple:
            id = partner_bank_tuple[0]
            bank_obj = self.pool.get('res.partner.bank')
            result = bank_obj.browse(self.cr, self.uid, [id], context=self.context)[0]
        return result
    
    def tax_summary(self):
        result = True
        result = self.datas.has_key('form') and self.datas['form'].get('tax_summary', result)   
        return result
