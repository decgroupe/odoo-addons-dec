from openupgradelib import openupgrade


def move_pack_x_line(env, version, table):
    cr = env.cr
    if openupgrade.table_exists(cr, table):
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE product_pack_line
            DROP CONSTRAINT IF EXISTS product_pack_line_product_uniq""",
        )
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
                {};
            """.format(table)
        )
        cr.execute("DROP TABLE {};".format(table))


@openupgrade.migrate()
def migrate(env, version):
    move_pack_x_line(env, version, 'product_pack_saleline')
    move_pack_x_line(env, version, 'product_pack_purchaseline')
