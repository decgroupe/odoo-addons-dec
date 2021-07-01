# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2021

from odoo import api, models, fields


class Project(models.Model):
    _inherit = "project.project"

    partner_shipping_id = fields.Many2one(
        'res.partner',
        compute='_compute_partner_shipping_id',
        string="Shipping Partner",
        readonly=True,
        store=True,
    )
    partner_shipping_zip_id = fields.Many2one(
        'res.city.zip',
        related='partner_shipping_id.zip_id',
        string="Shipping Partner's ZIP",
        readonly=True,
        store=True,
    )
    partner_shipping_country_id = fields.Many2one(
        'res.country',
        related='partner_shipping_id.country_id',
        string="Shipping Partner's Country",
        store=True,
    )

    @api.multi
    @api.depends('sale_order_id', 'name')
    def _compute_partner_shipping_id(self):
        for rec in self:
            if rec.sale_order_id:
                rec.partner_shipping_id = rec.sale_order_id.partner_shipping_id
            elif rec.name:
                sale_id = self.env['sale.order'].search(
                    [('name', '=', rec.name)], limit=1
                )
                if sale_id:
                    rec.partner_shipping_id = sale_id.partner_shipping_id

    @api.multi
    @api.depends('partner_shipping_id', 'partner_shipping_zip_id')
    def _get_name_identifications(self):
        res = super()._get_name_identifications()
        # Add partner and its location to quickly identify a contract
        if self.partner_shipping_id:
            name = ('👷 %s') % (self.partner_shipping_id.display_name, )
            res.append(name)
        if self.partner_shipping_zip_id:
            name = ('🗺️ %s') % (self.partner_shipping_zip_id.display_name, )
            res.append(name)
        return res
