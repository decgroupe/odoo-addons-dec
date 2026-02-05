# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResCity(models.Model):
    _inherit = "res.city"

    _sql_constraints = [
        (
            "name_state_country_uniq",
            "Check(1=1)",
            "Invalid constraint disabled",
        ),
    ]
