# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResCity(models.Model):
    _inherit = "res.city"

    _sql_constraints = [
        (
            "name_state_country_uniq",
            "Check(1=1)",
            "Invalid constraint disabled",
        ),
    ]

    @api.onchange("state_id")
    def _onchange_state(self):
        domain = []
        if self.state_id:
            domain = [("state_id", "=", self.state_id.id)]
            if not self.country_id:
                self.country_id = self.state_id.country_id
        return {"domain": {"department_id": domain}}
