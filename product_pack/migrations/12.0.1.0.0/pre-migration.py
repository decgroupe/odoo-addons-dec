from openupgradelib import openupgrade

column_renames = {
    'product_product': [
        ('stock_depends', None),
        #('sale_pack_line_ids', None), # Ignore One2Many
        ('fixed_sale_price', None),
        #('purchase_pack_line_ids', None), # Ignore One2Many
        ('fixed_purchase_price', None),
    ],
}

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
