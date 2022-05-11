# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

import logging

from openupgradelib import openupgrade
from odoo import SUPERUSER_ID, api, exceptions

_logger = logging.getLogger(__name__)

column_renames = {
    'product_template':
        [
            ('market_bom_id', None),
            ('market_markup_rate', None),
            ('market_material_cost_factor', None),
        ],
}

def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
