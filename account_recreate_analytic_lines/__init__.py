# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from . import models

import logging

_logger = logging.getLogger(__name__)


def post_init(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    invoice_ids = env['account.invoice'].search(
        [('state', 'not in', ['cancel'])]
    )
    invoice_ids.action_set_default_analytic_account()
