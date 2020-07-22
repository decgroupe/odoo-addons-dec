from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'crm_helpdesk'):
        pass
