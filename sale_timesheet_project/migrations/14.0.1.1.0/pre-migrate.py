from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "project_task", "exclude_from_sale_order"
    ):
        openupgrade.copy_columns(
            env.cr,
            {
                "project_task": [
                    ("non_allow_billable", "exclude_from_sale_order", None),
                ],
            },
        )
