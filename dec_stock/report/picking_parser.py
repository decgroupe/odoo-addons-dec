##############################################################################
#
#
##############################################################################

from report import report_sxw
from report.report_sxw import rml_parse
from tools.translate import _

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_message':self.get_message,
            'get_partner_address':self.get_partner_address,
            'get_production_order':self.get_production_order,
            'get_selection_value':self.get_selection_value,
            'get_origin_creator':self.get_origin_creator,
        })
        self.context = context
        
   
    def get_message(self, data):
        if data.has_key('form') and data['form'].has_key('message'):
            return data['form']['message']
        else:
            return ''
        
    def get_production_order(self, picking):
        production_obj = self.pool.get('mrp.production')
        production_ids = production_obj.search(self.cr, self.uid, [('picking_id.id', '=', picking.id )], context=self.context)
        
        if production_ids:
            production = production_obj.browse(self.cr, self.uid, production_ids, context=self.context)[0]
            return production.name
        else:
            return ''
        
    def get_partner_address(self, partner, address, extended = False):
        
        res = ''
        if partner:
            res += partner.name + '\n'
        
        if not partner or (partner.name <> address.name):
            if address.title: 
                res += address.title.name + ' '
            if address.name: 
                res += address.name
            if address.title or address.name: 
                res += '\n'
        
        if address.street: 
            res += address.street + '\n'
        if address.street2: 
            res += address.street2 + '\n'
               
        if address.zip: 
            res += address.zip + ' '
        if address.city: 
            res += address.city.upper()
        if address.zip or address.name: 
            res += '\n'
               
        if address.state_id: 
            res += address.state_id.name + ' '
        if address.country_id: 
            res += address.country_id.name.upper()
        if address.state_id or address.country_id: 
            res += '\n'
            
        if extended:           
            if address.phone: 
                res += _('Phone: ') + address.phone + '\n'
            if address.fax: 
                res += _('Fax: ') + address.fax + '\n'
            if partner and partner.vat: 
                res += _('VAT: ') + partner.vat + '\n'
               
        if res.endswith('\n'):
            res = res[0:-1]
                
        return res

    def get_selection_value(self, model, fieldName, field_val):
        return dict(self.pool.get(model).fields_get(self.cr, self.uid, context=self.context)[fieldName]['selection'])[field_val]

    def get_origin_creator(self, picking):
        picking_ids = []
        picking_obj = self.pool.get('stock.picking')
        
        if picking:
            picking_ids = picking_obj.search(self.cr, self.uid, [('backorder_id.id', '=', picking.id )], context=self.context)
        
        if picking_ids:
            return self.get_origin_creator(picking_obj.browse(self.cr, self.uid, picking_ids[0], context=self.context))
        else:
            if picking.create_uid:
                return picking.create_uid.name
            else:
                return False
