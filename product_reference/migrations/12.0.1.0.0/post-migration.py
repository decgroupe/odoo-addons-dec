from openupgradelib import openupgrade

columns = [
    'ciel_code',
    'comments',
    'market_bom_id',
    'market_markup_rate',
    'market_material_cost_factor',
    'public_code',
    'internal_notes',
]


@openupgrade.migrate()
def migrate(env, version):
    legacy_mapping = [(x, openupgrade.get_legacy_name(x)) for x in columns]

    mapping_str = []
    for item in legacy_mapping:
        if openupgrade.column_exists(env.cr, 'product_product', item[1]):
            new_col_name = item[0]
            # Force new names since framework will create column with these
            # names.
            if new_col_name == 'ciel_code':
                new_col_name = 'public_code'
            if new_col_name == 'comments':
                new_col_name = 'internal_notes'

            mapping_str.append('{0}=pp.{1}'.format(new_col_name, item[1]))

    print(legacy_mapping)
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template pt SET
            {0}
        FROM product_product pp
        WHERE pt.id = pp.id
        """.format(','.join(mapping_str))
    )
