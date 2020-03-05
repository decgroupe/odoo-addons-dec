from openupgradelib import openupgrade

# _model_renames = [
#     ('account.asset.category', 'account.asset.profile'),
#     ('account.asset.depreciation.line', 'account.asset.line'),
#     ('account.asset.asset', 'account.asset'),
# ]

# _table_renames = [
#     (old.replace('.', '_'), new.replace('.', '_'))
#     for (old, new) in _model_renames
# ]

# _column_copies = {
#     'account_asset': [
#         ('method_number', None, None),
#         ('method_time', None, None),
#     ],
#     'account_asset_profile': [
#         ('method_number', None, None),
#         ('method_time', None, None),
#     ],
# }

# _column_renames = {
#     'account_asset': [
#         ('method_period', None),
#     ],
#     'account_asset_profile': [
#         ('method_period', None),
#     ],
# }

# _field_renames = [
#     ('account.asset', 'account_asset', 'category_id', 'profile_id'),
#     ('account.asset', 'account_asset', 'currency_id', 'company_currency_id'),
#     ('account.asset', 'account_asset', 'date', 'date_start'),
#     ('account.asset', 'account_asset', 'value', 'purchase_value'),
#     ('account.asset.line', 'account_asset_line',
#      'depreciation_date', 'line_date'),
#     ('account.asset.profile', 'account_asset_profile',
#      'account_depreciation_expense_id', 'account_expense_depreciation_id'),
#     ('account.invoice.line', 'account_invoice_line',
#      'asset_category_id', 'asset_profile_id'),

column_renames = {
    'product_product': [
        ('ciel_code', None),
        ('comments', None),
        ('market_bom_id', None),
        ('market_markup_rate', None),
        ('market_material_cost_factor', None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, column_renames)
