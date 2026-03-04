# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020


from odoo import api, fields, models


class RefCategory(models.Model):
    _name = "ref.category"
    _description = "Category"
    _rec_name = "name"
    _rec_names_search = ["name", "code"]
    _order = "code"

    code = fields.Char(
        string="Code",
        required=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )
    product_category_id = fields.Many2one(
        comodel_name="product.category",
        string="Product category",
    )
    description_template = fields.Text(
        string="Template",
        help="This text is used to automatically generate the product "
        "description based on its properties",
        required=False,
    )
    category_line_ids = fields.One2many(
        comodel_name="ref.category.line",
        inverse_name="category_id",
        string="Category Lines",
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Code category must be unique !"),
    ]

    def _prepare_product_category_vals(self, cat_vals):
        parent_categ_id = self.env.user.company_id.main_product_category_id
        return {
            "name": cat_vals.get("name"),
            "parent_id": parent_categ_id.id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product_category_id = vals.get("product_category_id")
            if not product_category_id:
                product_category_vals = self._prepare_product_category_vals(vals)
                product_category = self.env["product.category"].create(
                    product_category_vals
                )
                vals["product_category_id"] = product_category.id
        category_ids = super().create(vals_list)
        return category_ids

    def write(self, vals):
        name = vals.get("name")
        if name:
            for rec in self.filtered("product_category_id"):
                if rec.product_category_id.name == self.name:
                    rec.product_category_id.name = name
        res = super().write(vals)
        return res

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get("code"):
            default["code"] = self.env._("%(code)s (copy)", code=self.code)
        reference_id = super().copy(default)
        return reference_id

    @api.onchange("code")
    def onchange_code(self):
        if self.code:
            self.code = self.code.upper()

    @api.depends("name", "code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}"
