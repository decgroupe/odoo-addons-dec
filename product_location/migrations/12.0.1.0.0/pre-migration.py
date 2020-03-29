from openupgradelib import openupgrade

table = 'product_template'
column_renames = {
    table:
        [
            ('openupgrade_legacy_9_0_loc_case', 'loc_case'),
            ('openupgrade_legacy_9_0_loc_rack', 'loc_rack'),
            ('openupgrade_legacy_9_0_loc_row', 'loc_row'),
        ],
}


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    # Restore columns disabled on 8.0 -> 9.0 migration
    for row in column_renames[table]:
        if openupgrade.column_exists(cr, table, row[0]):
            if openupgrade.column_exists(cr, table, row[1]):
                row1 = [(table, row[1])]
                openupgrade.drop_columns(cr, row1)
                columns = {table: [(row[0], row[1])]}
                openupgrade.rename_columns(cr, columns)
