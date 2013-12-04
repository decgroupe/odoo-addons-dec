##############################################################################
#
#
##############################################################################

import pooler
import time
from report import report_sxw
from report.report_sxw import rml_parse
from tools.translate import _

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'ids_to_objects': self._ids_to_objects,
            'get_partner_address':self.get_partner_address,
            'adr_get': self._adr_get,
            'lines_get': self._lines_get,
            'message_get': self._message_get
        })
        self.context = context

    def _ids_to_objects(self, ids):
        pool = pooler.get_pool(self.cr.dbname)
        all_lines = []
        index = 0
        for line in pool.get('account_followup.stat.by.partner').browse(self.cr, self.uid, ids):
            if line not in all_lines:
                line.index = index
                all_lines.append(line)
                index += 1
        return all_lines
    
    def _adr_get(self, partner_id, type):
        res_partner = pooler.get_pool(self.cr.dbname).get('res.partner')
        res_partner_address = pooler.get_pool(self.cr.dbname).get('res.partner.address')
        adr = res_partner.address_get(self.cr, self.uid, [partner_id.id], [type])[type]
        return adr and res_partner_address.browse(self.cr, self.uid, [adr], context = self.context)[0] or None

    def get_partner_address(self, partner, address, extended = False):
        
        res = ''
        if partner:
            res += partner.name + '\n'
        
        if address:
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
            if address and address.phone: 
                res += _('Phone: ') + address.phone + '\n'
            if address and address.fax: 
                res += _('Fax: ') + address.fax + '\n'
            if partner and partner.vat: 
                res += _('VAT: ') + partner.vat + '\n'
               
        if res.endswith('\n'):
            res = res[0:-1]
                
        return res
    

    def _lines_get(self, stat_line):
        pool = pooler.get_pool(self.cr.dbname)
        moveline_obj = pool.get('account.move.line')
        company_obj = pool.get('res.company')
        obj_currency =  pool.get('res.currency')
        
        movelines_ids = moveline_obj.search(self.cr, self.uid,
                [('partner_id', '=', stat_line.partner_id.id),
                 ('account_id.type', '=', 'receivable'),
                 ('reconcile_id', '=', False), 
                 ('state', '<>', 'draft'),
                 ('company_id','=', stat_line.company_id.id)], context=self.context)
        
        movelines = moveline_obj.browse(self.cr, self.uid, movelines_ids, context=self.context)
        base_currency = movelines[0].company_id.currency_id
        final_res = []
        line_cur = {base_currency.id: {'line': []}}
        res = []

        for line in movelines:
            '''
            if line.currency_id and (not line.currency_id.id in line_cur):
                line_cur[line.currency_id.id] = {'line': []}
            '''
            currency = line.currency_id or line.company_id.currency_id
            '''
            line_data = {
                         'name': line.move_id.name,
                         'ref': line.ref,
                         'date':line.date,
                         'date_maturity': line.date_maturity,
                         'balance': currency.id <> line.company_id.currency_id.id and line.amount_currency or (line.debit - line.credit),
                         'blocked': line.blocked,
                         'currency_id': currency.symbol or currency.name,
                         }
            line_cur[currency.id]['line'].append(line_data)
            '''
            
            # YP Custom
            line.name = line.move_id.name
            line.balance = currency.id <> line.company_id.currency_id.id and line.amount_currency or (line.debit - line.credit)
            line.currency_id = currency.symbol or currency.name
            res.append(line)
        '''
        for cur in line_cur:
            if line_cur[cur]['line']:
                final_res.append({'line': line_cur[cur]['line']})
        return final_res
        '''
        return res



    def _message_get(self, stat_line, followup_id):
        fp_obj = pooler.get_pool(self.cr.dbname).get('account_followup.followup')
        fp_line = fp_obj.browse(self.cr, self.uid, followup_id).followup_line
        li_delay = []
        for line in fp_line:
            li_delay.append(line.delay)
        li_delay.sort(reverse=True)
        text = ""
        a = {}
        partner_line_ids = pooler.get_pool(self.cr.dbname).get('account.move.line').search(self.cr, self.uid, [('partner_id','=',stat_line.partner_id.id),('reconcile_id','=',False),('company_id','=',stat_line.company_id.id)])
        partner_delay = []
        #context.update({'lang': stat_line.partner_id.lang})
        for i in pooler.get_pool(self.cr.dbname).get('account.move.line').browse(self.cr, self.uid, partner_line_ids, self.context):
            for delay in li_delay:
                if  i.followup_line_id and str(i.followup_line_id.delay)==str(delay):
                    text = i.followup_line_id.description
                    a[delay] = text
                    partner_delay.append(delay)
        text = partner_delay and a[max(partner_delay)] or ''
        if text:
            text = text % {
                'partner_name': stat_line.partner_id.name,
                'date': time.strftime('%Y-%m-%d'),
                'company_name': stat_line.company_id.name,
                'user_signature': pooler.get_pool(self.cr.dbname).get('res.users').browse(self.cr, self.uid, self.uid, self.context).signature or '',
            }

        return text
    
