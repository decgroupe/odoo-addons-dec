# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class ResPartnerAcademy(models.Model):
    """ Description """

    _name = 'res.partner.academy'
    _description = 'Academy'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Text('Name', required=True)

