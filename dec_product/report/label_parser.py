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
            'manufacturer': self.get_manufacturer,
            'hello_world':self.hello_world,
        })
        self.context = context

    def hello_world(self, name):
        return "Hello, %s!" % name

    def get_manufacturer(self, product):
        res = ''
        categ_id = product.categ_id
        if categ_id:
            while categ_id.parent_id and (categ_id.parent_id.id <> 1):
                categ_id = categ_id.parent_id

            if categ_id <> product.categ_id:
                res = ('%s - %s') % (categ_id.name, product.categ_id.name)
            else:
                res = ('%s') % (categ_id.name) 

        return res

