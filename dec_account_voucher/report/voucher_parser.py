# -*- coding: utf-8 -*-
from report import report_sxw
from report.report_sxw import rml_parse

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'sum_lines': self.sum_lines,
            'should_print_debit_lines': self.should_print_debit_lines,
            'should_print_debit_line_at_0': self.should_print_debit_line_at_0,
            'should_print_credit_lines': self.should_print_credit_lines,
            'should_print_credit_line_at_0': self.should_print_credit_line_at_0,
            'get_partner_address_by_type': self.get_partner_address_by_type,
            'print_address_type': self.print_address_type,
            'print_partner_address_by_type': self.print_partner_address_by_type,
            'print_partner_address': self.print_partner_address,
        })
        self.context = context

    def sum_lines(self, lines):
        result = 0
        for line in lines:
            result += line.amount
        return result

    def should_print_debit_lines(self, lines):
        result = self.sum_lines(lines) > 0
        if result and self.datas.has_key('form'):
            result = self.datas['form'].get('should_print_debit_lines', result)
        return result

    def should_print_debit_line_at_0(self, line):
        result = True
        if self.datas.has_key('form'):
            if line.amount == 0:
                result = self.datas['form'].get('should_print_debit_line_at_0', result)
        return result
        
    def should_print_credit_lines(self, lines):
        result = self.sum_lines(lines) > 0
        if result and self.datas.has_key('form'):
            result = self.datas['form'].get('should_print_credit_lines', result)
        return result

    def should_print_credit_line_at_0(self, line):
        result = True
        if self.datas.has_key('form'):
            if line.amount == 0:
                result = self.datas['form'].get('should_print_credit_line_at_0', result)
        return result
        
    def get_partner_address_by_type(self, partner_id, address_type):
        result = False
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        addresses = partner_obj.address_get(self.cr, self.uid, [partner_id.id], [address_type])
        if addresses:
            id = addresses[address_type] 
            address_id = address_obj.browse(self.cr, self.uid, [id], context = self.context)[0]
            result = address_id
        return result

    def print_address_type(self, address_type):
        result = 'Adresse:'
        if address_type == 'invoice':
            result = 'Adresse de facturation:'
        if address_type == 'delivery':
            result = 'Adresse de livraison:'
        if address_type == 'contact':
            result = 'Adresse de contact:'
        return result

    def print_partner_address_by_type(self, partner_id, address_type):
        result = ''
        address_id = self.get_partner_address_by_type(partner_id, address_type)
        if address_id:
            result = self.print_partner_address(partner_id, address_id)
        return result

    def print_partner_address(self, partner_id, address_id):
        
        # Create a static class to store local variables accessible 
        # from nested functions
        class local:
            result = ''
            newline = False
            last_level = 0

        def add_new_line(level):
            if local.newline and level > local.last_level: 
                while local.newline: 
                    local.last_level = level
                    local.result += '\n'
                    if isinstance(local.newline, int):
                        local.newline -= 1
                    else:
                        local.newline = False

        if partner_id:
            local.result += partner_id.name
            local.newline = True
        if address_id:
            if address_id.title:
                add_new_line(1)
                local.result += address_id.title.name + ' '
                local.newline = True
            if address_id.name:
                add_new_line(1)
                local.result += address_id.name
                local.newline = True
            if address_id.street:
                add_new_line(2)
                local.result += address_id.street
                local.newline = True
            if address_id.street2:
                add_new_line(3)
                local.result += address_id.street2
                local.newline = True
            if address_id.zip:
                add_new_line(4)
                local.result += address_id.zip + ' '
                local.newline = True
            if address_id.city:
                add_new_line(4)
                local.result += address_id.city.upper()
                local.newline = True
            if address_id.state_id:
                add_new_line(5)
                local.result += address_id.state_id.name.upper() + ' '
                local.newline = True
            if address_id.country_id:
                add_new_line(5)
                local.result += address_id.country_id.name.upper()
                local.newline = True
            local.newline = 2
            if address_id.phone:
                add_new_line(6)
                local.result += u'Tél.: ' + address_id.phone
                local.newline = True
            if address_id.fax:
                add_new_line(7)
                local.result += 'Fax: ' + address_id.fax
                local.newline = True
        if partner_id and partner_id.vat:
            add_new_line(8)
            local.result +=  'TVA: ' + partner_id.vat

        return local.result

