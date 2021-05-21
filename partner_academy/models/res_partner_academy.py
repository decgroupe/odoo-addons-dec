# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class ResPartnerAcademy(models.Model):
    """ National Education Academy """

    _name = 'res.partner.academy'
    _description = 'Academy'
    _rec_name = 'name'
    _order = 'name'

    partner_id = fields.Many2one('res.partner', 'Rectorate')
    name = fields.Text('Name', required=True)
    email_domain = fields.Char(
        help="Filling this domain (part after the @) will help to "
        "quickly identify a partner academy using its e-mail suffix"
    )
    logo = fields.Binary(
        related='partner_id.image',
        string="Academy Logo",
        readonly=False,
    )
    state_id = fields.Many2one(
        "res.country.state",
        related="partner_id.state_id",
        string='State',
        readonly=False,
    )
    country_id = fields.Many2one(
        "res.country",
        related="partner_id.country_id",
        string='Country',
    )
