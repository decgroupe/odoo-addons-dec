# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

import logging

from openupgradelib import openupgrade
from odoo import SUPERUSER_ID, api, exceptions

_logger = logging.getLogger(__name__)

column_renames = {
    'ref_market_bom':
        [
            ('name', None),
            ('product_uom_id', None),
            ('product_qty', None),
            ('bom_id', None),
            ('partner_id', None),
            ('locked_price', None),
            ('price', None),
        ],
}


def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
