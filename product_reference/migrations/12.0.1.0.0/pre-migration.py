from openupgradelib import openupgrade

PRODUCT = 'product_product'

column_renames = {
    PRODUCT:
        [
            ('market_bom_id', None),
            ('market_markup_rate', None),
            ('market_material_cost_factor', None),
        ],
}

column_renames_old = {
    PRODUCT: [
        ('ciel_code', None),
        ('comments', None),
    ],
}

column_renames_new = {
    PRODUCT: [
        ('public_code', None),
        ('internal_notes', None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
        env.cr, PRODUCT, column_renames[PRODUCT][0][0]
    ):
        openupgrade.rename_columns(env.cr, column_renames)

    if openupgrade.column_exists(
        env.cr, PRODUCT, column_renames_old[PRODUCT][0][0]
    ):
        openupgrade.rename_columns(env.cr, column_renames_old)

    if openupgrade.column_exists(
        env.cr, PRODUCT, column_renames_new[PRODUCT][0][0]
    ):
        openupgrade.rename_columns(env.cr, column_renames_new)