# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class RefLog(models.Model):
    """ Reference log for all operations """

    _name = 'ref.log'
    _description = 'Log'
    _rec_name = 'operation'
    _order = 'id desc'

    operation = fields.Text('Operation', required=True)
    username = fields.Text('User', required=True)
    localcomputername = fields.Text('Computer', required=True)
    localusername = fields.Text('Local Username', required=True)
    ipaddress = fields.Text('IP Address', required=True)
    datetime = fields.Datetime('Modification date', default=fields.Datetime.now)
