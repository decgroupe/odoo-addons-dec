# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Move public_code storage to product variants and keep legacy column."""
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE product_product
        ADD COLUMN IF NOT EXISTS public_code varchar(24)
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE product_product AS pp
        SET public_code = pt.public_code
        FROM product_template AS pt
        WHERE pt.id = pp.product_tmpl_id
        AND pt.public_code IS NOT NULL
        """,
    )
    if openupgrade.column_exists(cr, "product_template", "public_code"):
        openupgrade.rename_columns(
            cr,
            {"product_template": [("public_code", None)]},
        )
