from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    sol_ids = env["sale.order.line"].search(
        [
            ("product_id.service_tracking", "=", "create_application_pass"),
        ]
    )
    sol_ids.qty_delivered_method = "application_pass"
    pass
