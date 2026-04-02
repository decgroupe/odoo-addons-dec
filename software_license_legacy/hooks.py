# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Update system computed fields for all existing software licenses."""
    _logger.info("Update systems")
    # Update stages
    license_ids = env["software.license"].search([])
    license_ids._compute_system()
