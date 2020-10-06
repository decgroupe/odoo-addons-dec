# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, models


class WebEnvironmentRibbonBackend(models.AbstractModel):
    _inherit = 'web.environment.ribbon.backend'

    @api.model
    def get_environment_ribbon(self):
        """
        This method returns the ribbon data from ir config parameters
        :return: dictionary
        """
        res = super().get_environment_ribbon()
        if self.env.cr.dbname in ['dec', 'esi']:
            res['name'] = ''
        return res
