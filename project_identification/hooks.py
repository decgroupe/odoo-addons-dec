# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Update is_time_tracking and is_contract")
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Update stages
    project_ids = env["project.project"].search([])
    project_ids._compute_from_type()
