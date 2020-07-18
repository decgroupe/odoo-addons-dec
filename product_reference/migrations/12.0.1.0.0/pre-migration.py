from openupgradelib import openupgrade

column_renames = {
    'product_product':
        [
            ('ciel_code', None),
            ('comments', None),
            ('market_bom_id', None),
            ('market_markup_rate', None),
            ('market_material_cost_factor', None),
        ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
