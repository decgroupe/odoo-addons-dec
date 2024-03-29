# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_zip_id = fields.Many2one(
        comodel_name='res.city.zip',
        related='partner_id.zip_id',
        string="ZIP Location",
        store=True,
    )
    partner_city_id = fields.Many2one(
        comodel_name='res.city',
        related='partner_id.city_id',
        string="Partner's City",
        store=True,
    )

    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delivery Address',
        help="Delivery address for created sales order.",
        track_visibility='onchange',
        track_sequence=2,
    )
    partner_shipping_country_id = fields.Many2one(
        comodel_name='res.country',
        related='partner_shipping_id.country_id',
        string="Shipping Partner's Country",
        readonly=True,
        store=True,
    )
    partner_shipping_zip_id = fields.Many2one(
        comodel_name='res.city.zip',
        related='partner_shipping_id.zip_id',
        string="Shipping Partner's ZIP",
        store=True,
    )
    partner_shipping_city_id = fields.Many2one(
        comodel_name='res.city',
        related='partner_shipping_id.city_id',
        string="Shipping Partner's City",
        store=True,
    )

    def _onchange_partner_id_values(self, partner_id):
        result = super()._onchange_partner_id_values(partner_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            addr = partner.address_get(['delivery'])
            result["partner_shipping_id"] = addr['delivery']
        return result

    @api.multi
    def _convert_opportunity_data(self, customer, team_id=False):
        values = super()._convert_opportunity_data(customer, team_id)
        if customer:
            addr = customer.address_get(['delivery'])
            values["partner_shipping_id"] = addr['delivery']
        return values
