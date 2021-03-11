# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _is_subcontracted_service(self, product_id):
        return (
            product_id.type == 'service' and product_id.service_to_purchase and
            product_id.purchase_ok or False
        )
