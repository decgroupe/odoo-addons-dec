from openupgradelib import openupgrade

_table_renames = [
    ('product_pack_saleline', 'product_pack_line'),
]

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'product_pack_saleline'):
        if openupgrade.table_exists(cr, 'product_pack_line'):
            cr.execute("DROP TABLE product_pack_line;")
        openupgrade.rename_tables(cr, _table_renames)

    if openupgrade.table_exists(cr, 'product_pack_purchaseline'):
        cr.execute(
            """
            INSERT INTO product_pack_line
            (
                create_uid, create_date, write_date, write_uid, 
                quantity, product_id, parent_product_id
            )
            SELECT 
                create_uid, create_date, write_date, 
                write_uid, quantity, product_id, parent_product_id
            FROM 
                product_pack_purchaseline;
            """)
        cr.execute("DROP TABLE product_pack_purchaseline;")
