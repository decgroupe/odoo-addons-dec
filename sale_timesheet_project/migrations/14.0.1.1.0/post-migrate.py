from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    time_tracking_type_id = env.ref("project_identification.time_tracking_type")
    domain = [
        "|",
        ("sale_line_id", "=", False),
        ("type_id", "=", time_tracking_type_id.id)
    ]
    task_ids = env["project.task"].search(domain)
    task_ids.write(
        {
            "exclude_from_sale_order": True,
        }
    )

    contract_type = env.ref("project_identification.contract_type")
    domain = [("type_id", "=", contract_type.id)]
    project_ids = env["project.project"].search(domain)
    project_ids.write(
        {
            "allow_billable": True,
            "bill_type": "customer_project",
            "pricing_type": "fixed_rate",
        }
    )
    for project_id in project_ids:
        if not project_id.sale_order_id and len(project_id.contract_ids) == 1:
            contract_id = project_id.contract_ids
            if contract_id.state in ("done", "sale"):
                project_id.sale_order_id = contract_id
