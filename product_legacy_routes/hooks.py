# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import logging

_logger = logging.getLogger(__name__)


def uninstall_hook(env):
    pass


def post_init_hook(env):
    mto_route = env.ref("stock.route_warehouse0_mto")
    mto_route.active = True
