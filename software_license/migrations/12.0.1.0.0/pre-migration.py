from openupgradelib import openupgrade

_model_renames = [
    ('licence.licence', 'software.license'),
    ('licence.application', 'software.license.application'),
]

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'licence_licence'):
        openupgrade.rename_models(cr, _model_renames)
