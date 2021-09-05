# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2021

import requests
import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class HealthchecksPing(models.Model):
    "Static class to make ping to an healthchecks.io server"
    _name = 'healthchecks.ping'
    _description = 'Healthchecks Ping'

    @api.model
    def action_ping_custom_url(self, url):
        try:
            requests.post(url, timeout=10, json=self._get_ping_data())
        except requests.RequestException as e:
            # Log ping failure here...
            _logger.error("Ping failed: %s" % e)

    @api.model
    def action_ping_config_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param(
            'healthchecks.url', False
        )
        self.action_ping_custom_url(url),

    @api.model
    def _get_ping_data(self):
        return {
            "database": self.env.cr.dbname,
        }
