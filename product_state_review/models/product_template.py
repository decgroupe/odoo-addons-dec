from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        # Auto set state to obsolete when archiving a product
        if "active" in vals and not vals.get("active"):
            vals["state"] = "obsolete"
        res = super().write(vals)
        return res
