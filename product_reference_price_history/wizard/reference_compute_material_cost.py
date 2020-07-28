# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class ReferenceComputeMaterialCost(models.TransientModel):
    _inherit = 'wizard.run'
    _name = 'reference.compute_material_cost'
    _description = 'Compute Material Cost Manually'

    def execute(self):
        self.env['ref.reference'].run_material_cost_scheduler(
            # use_new_cursor=self._cr.dbname, company_id=company.id
        )
