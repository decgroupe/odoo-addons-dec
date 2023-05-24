# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Update production stages")
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Update stages
    production_ids = env["mrp.production"].search([])
    production_ids._compute_stage_id()
