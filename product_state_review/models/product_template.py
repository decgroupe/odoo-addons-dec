from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    state = fields.Selection(
        selection=[
            ("quotation", "In Quotation"),
            ("draft", "In Development"),
            ("review", "Need review"),
            ("sellable", "Normal"),
            ("end", "End of Lifecycle"),
            ("obsolete", "Obsolete"),
        ],
        string="Status",
        default="sellable",
        index=True,
        tracking=True,
    )

    def write(self, vals):
        # Auto set state to obsolete when archiving a product
        if "active" in vals and not vals.get("active"):
            vals["state"] = "obsolete"
        res = super().write(vals)
        return res
