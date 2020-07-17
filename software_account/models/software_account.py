# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class SoftwareAccount(models.Model):
    _name = 'software.account'
    _description = 'Software Account'
    _rec_name = 'login'
    _order = 'id desc'

    supplier_id = fields.Many2one(
        'software.account.supplier', 'Supplier', required=True
    )
    login = fields.Char('Login', size=64, required=True)
    password = fields.Char('Password', size=64, required=True)
    email = fields.Char('E-Mail', size=64, required=True)
    firstname = fields.Char('Firstname', size=64)
    lastname = fields.Char('Lastname', size=64)
    question = fields.Text('Question')
    answer = fields.Text('Answer')
    pin = fields.Char('Pin Code', size=16)
    product_id = fields.Many2one(
        'product.product', 'Product', domain=[], change_default=True
    )
    production_id = fields.Many2one('mrp.production', 'Production')
    partner_id = fields.Many2one('res.partner', 'Partner')
    datetime = fields.Datetime('Modification date', default=fields.Datetime.now)
    info = fields.Text('Informations')

    @api.multi
    def _get_aeroo_report_filename(self):
        names = [x.name for x in self]
        res = '-'.join(names)
        return res
