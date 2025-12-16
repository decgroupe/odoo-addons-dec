from openupgradelib import openupgrade

from odoo.tools.sql import column_exists

column_renames = {
    "project_project": [("default_task_user_id", "old_default_task_user_id")],
}


@openupgrade.migrate()
def migrate(env, version):
    """Rename the column to keep the old value."""
    if column_exists(env.cr, "project_project", "default_task_user_id"):
        openupgrade.rename_columns(env.cr, column_renames)
