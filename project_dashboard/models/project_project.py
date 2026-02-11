# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021


from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"
    _order = "dashboard_sequence desc, sequence, name, id"

    type_date = fields.Date(
        string="Type Date",
        compute="_compute_type_date",
        store=True,
        help="Date used as reference for computing projects count per year on "
        "dashboard. It is a copy of the date field defined on project type, but "
        "stored on project to be able to use it in search domain, group by and views.",
    )
    dashboard_sequence = fields.Integer(
        string="Dashboard Position",
        default=0,
        help="If set, then this project will be displayed on the "
        "dashboard. A higher value indicats an higher priority.",
    )

    kanban_description = fields.Char(compute="_compute_kanban_description")

    def write(self, vals):
        result = super().write(vals)
        if result:
            date_fields = self.mapped("type_id").mapped("date_field")
            # check if one of the `date_fields` is in vals, if yes, then update
            # `type_date` for all projects
            if any(date_field in vals for date_field in date_fields):
                self._compute_type_date()
        return result

    def _compute_kanban_description(self):
        for rec in self:
            rec.kanban_description = rec.partner_shipping_id.display_name

    @api.depends("type_id", "type_id.date_field")
    def _compute_type_date(self):
        for rec in self:
            date_field = rec.type_id.date_field
            if date_field and date_field in rec._fields:
                rec.type_date = getattr(rec, date_field, False)
            else:
                # fallback on `create_date` if no `type_id` or `date_field` defined
                rec.type_date = rec.create_date
