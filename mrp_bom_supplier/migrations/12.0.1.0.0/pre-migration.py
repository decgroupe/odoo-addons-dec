from openupgradelib import openupgrade


@openupgrade.progress()
def migrate_progress(env, cr):
    if openupgrade.column_exists(cr, 'mrp_bom', 'name'):
        cr.execute(
            """
            UPDATE 
                mrp_bom
            SET 
                code=name;
        """
        )
        openupgrade.drop_columns(cr, [
            ('mrp_bom', 'name'),
        ])


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    migrate_progress(env, cr)
