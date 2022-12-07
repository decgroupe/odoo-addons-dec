# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

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
        related='partner_id.image_1920',
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
    department_ids = fields.Many2many(
        'res.country.department',
        string='Departments',
        help='Departments of this academy',
        domain="[('country_id', '=', country_id), ('state_id', '=', state_id)]",
    )

