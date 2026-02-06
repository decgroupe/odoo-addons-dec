# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    """Copy content from custom 'comments' column to built-in 'description' column.

    In 18.0, Odoo added a native 'description' (Internal Notes) field to hr.expense.
    This module previously defined a custom 'comments' field for the same purpose.
    We copy the data before the upgrade so nothing is lost when the column is dropped.
    """
    if not column_exists(env.cr, "hr_expense", "comments"):
        return
    env.cr.execute(
        """
        UPDATE hr_expense
        SET description = comments
        WHERE comments IS NOT NULL
          AND comments != ''
          AND (description IS NULL OR description = '')
        """
    )
