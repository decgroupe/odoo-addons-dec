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
            'hello_world':self.hello_world,
        })
        self.context = context

    def hello_world(self, name):
        return "Hello, %s!" % name

    def _current_subtotal(self, order, current_line):
        sum = 0
        for line in order.abstract_line_ids:
            sum = sum + line.price_subtotal
            if line == current_line:
                return sum
            elif line.layout_type == 'subtotal':
                sum = 0 
            
        return 0
        
