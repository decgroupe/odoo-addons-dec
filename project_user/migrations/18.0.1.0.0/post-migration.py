from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    if not column_exists(env.cr, "project_project", "old_default_task_user_id"):
        return

    openupgrade.m2o_to_x2m(
        env.cr,
        env["project.project"],
        "project_project",
        "default_task_user_ids",
        "old_default_task_user_id",
    )
