import json

from odoo import SUPERUSER_ID, api
from odoo.tools.safe_eval import safe_eval

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rec in (
        env["software.license.hardware"].with_context(active_test=False).search([])
    ):
        if rec.info:
            data = safe_eval(rec.info)
            rec.info = json.dumps(data, indent=4)
