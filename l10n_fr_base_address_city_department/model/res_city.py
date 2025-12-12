# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCity(models.Model):
    _inherit = "res.city"

    # override domain of the `state_id` domain to display states of the country
    # selected AND all states if no country is selected
    state_id = fields.Many2one(
        domain="[('country_id', '=?', country_id)]",
    )
    department_id = fields.Many2one(
        comodel_name="res.country.department",
        string="Department",
        help="Department of this city",
        domain="[('state_id', '=?', state_id)]",
    )

    @api.onchange("state_id")
    def _onchange_state(self):
        if self.state_id and not self.country_id:
            self.country_id = self.state_id.country_id

    @api.onchange("department_id")
    def _onchange_department(self):
        if self.department_id and not self.state_id:
            self.state_id = self.department_id.state_id
