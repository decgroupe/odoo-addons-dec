from openupgradelib import openupgrade

@openupgrade.progress()
def migrate_progress(env, cr):
    pass

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    migrate_progress(env, cr)