# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    pass


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mto_route = env.ref("stock.route_warehouse0_mto")
    mto_route.active = True
