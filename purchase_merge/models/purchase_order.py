# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_mergeable_states(self):
        return ('draft', 'sent', 'to approve')
