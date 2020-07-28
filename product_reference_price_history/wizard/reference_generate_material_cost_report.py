# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class ReferenceGenerateMaterialCostReport(models.TransientModel):
    _inherit = 'wizard.run'
    _name = 'reference.generate_material_cost_report'
    _description = 'Generate Material Cost Report'

    def execute(self):
        self.env['ref.reference'].generate_material_cost_report()
