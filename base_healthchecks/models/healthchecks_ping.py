# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2021

import socket
import requests
import json
import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)

def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """

    return "/".join(map(lambda x: str(x).rstrip('/'), args))

class HealthchecksPing(models.Model):
    "Static class to make ping to an healthchecks.io server"
    _name = 'healthchecks.ping'
    _description = 'Healthchecks Ping'

    @api.model
    def action_ping(self, url, data=None):
        res = False
        try:
            post_data = self._get_ping_data()
            if isinstance(data, dict):
                post_data.update(data)
            res = requests.post(url, timeout=10, json=post_data)
        except requests.RequestException as e:
            # Log ping failure here...
            _logger.error("Ping failed: %s" % e)
        return res

    @api.model
    def action_ping_start(self, url, data=None):
        return self.action_ping(urljoin(url, "start"), data)

    @api.model
    def action_ping_log(self, url, data=None):
        return self.action_ping(urljoin(url, "log"), data)

    @api.model
    def action_ping_fail(self, url, data=None):
        return self.action_ping(urljoin(url, "fail"), data)

    @api.model
    def action_ping_config_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param(
            'healthchecks.url', False
        )
        self.action_ping(url)

    @api.model
    def _get_ping_data(self):
        return {
            "hostname": socket.gethostname(),
            "database": self.env.cr.dbname,
        }
