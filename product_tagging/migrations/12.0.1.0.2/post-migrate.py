from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        """
        INSERT INTO tagging_product_tmpl (tag_id, product_tmpl_id)
        SELECT tag_id, product_id
        FROM tagging_product;
        """
    )
