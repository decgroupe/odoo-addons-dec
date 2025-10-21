# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCity(models.Model):
    _inherit = "res.city"

    department_id = fields.Many2one(
        comodel_name="res.country.department",
        string="Department",
        help="Department of this city",
    )

    @api.onchange("department_id")
    def _onchange_department(self):
        if self.department_id and not self.state_id:
            self.state_id = self.department_id.state_id
