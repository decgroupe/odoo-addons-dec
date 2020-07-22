# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import models, fields


class CrmHelpdesk(models.Model):
    _name = 'crm.helpdesk'
    _description = 'Dummy model for transition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
