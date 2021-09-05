# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_zip_id = fields.Many2one(
        'res.city.zip',
        related='partner_id.zip_id',
        string="ZIP Location",
        store=True,
    )
    partner_city_id = fields.Many2one(
        'res.city',
        related='partner_id.city_id',
        string="City",
        store=True,
    )
