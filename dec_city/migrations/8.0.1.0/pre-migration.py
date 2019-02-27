# -*- coding: utf-8 -*-

from openupgradelib import openupgrade


column_renames = {
    'city_city': [
        ('name', 'city'),
        ('zip', 'name'),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, [('city_city', 'res_better_zip')])
    openupgrade.rename_models(cr, [('city.city', 'res.better.zip')])

