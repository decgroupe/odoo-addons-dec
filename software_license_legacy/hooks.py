# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Update systems")
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Update stages
    license_ids = env["software.license"].search([])
    license_ids._compute_system()
