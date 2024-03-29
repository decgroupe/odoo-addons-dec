# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import models, api, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    ticket_identification = fields.Char(
        string="Ticket Identification",
        compute="_compute_ticket_identification",
    )

    @api.multi
    @api.depends('ticket_id')
    def _compute_ticket_identification(self):
        for rec in self.filtered('ticket_id'):
            identifications = rec.ticket_id._get_name_identifications()
            rec.ticket_identification = ' / '.join(identifications)
