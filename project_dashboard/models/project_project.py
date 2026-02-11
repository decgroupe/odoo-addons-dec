# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from lxml import etree

from odoo import _, api, fields, models

from odoo.addons.tools_miscellaneous.tools.webclient import set_view_mode_first
from odoo.addons.web.controllers.utils import clean_action


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
            rec.kanban_description = False  # rec.partner_shipping_id.display_name

    @api.depends("type_id", "type_id.date_field")
    def _compute_type_date(self):
        for rec in self:
            date_field = rec.type_id.date_field
            if date_field and date_field in rec._fields:
                rec.type_date = getattr(rec, date_field, False)
            else:
                # fallback on `create_date` if no `type_id` or `date_field` defined
                rec.type_date = rec.create_date

    def action_open_all_tasks(self, view_domain=False, view_type=False):
        action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
        act = clean_action(action, self.env)

        project_ids = self.ids
        # We cannot rely on `self.ids` as it depends of loaded data in the
        # web client (Expand Group or Load More UI actions), so we get back
        # the original domain copied in context and we make our own search
        # view_domain = self.env.context.get('view_domain')
        if view_domain:
            project_ids = self.search(view_domain).ids

        act["context"] = {}
        act["domain"] = [("project_id", "in", project_ids)]
        if view_type:
            act["views"] = set_view_mode_first(act["views"], view_type)

        return act

    def open_tasks(self):
        # Override active_id and active_ids because they are probably project
        # types
        self_active = self.with_context(
            active_id=self.id,
            active_ids=self.ids,
        )
        return super(ProjectProject, self_active).open_tasks()
