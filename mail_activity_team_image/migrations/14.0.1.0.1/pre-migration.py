from openupgradelib import openupgrade

_field_renames = [
    (
        "mail.activity.team",
        "mail_activity_team",
        "image",
        "image_1920",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "mail_activity_team", "image"):
        openupgrade.rename_fields(env, _field_renames)
