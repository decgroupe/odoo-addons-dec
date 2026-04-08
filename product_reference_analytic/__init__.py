# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from . import models

import logging

_logger = logging.getLogger(__name__)


def post_init(env):
    """Create income analytic accounts for all existing ref.category records."""
    Category = env["ref.category"]
    category_ids = Category.search([])
    category_ids.action_create_income_analytic_account()
