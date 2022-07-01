# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from lxml import etree

from odoo import _, api, fields, models
from odoo.addons.web.controllers.main import clean_action
from odoo.addons.tools_miscellaneous.tools.webclient import set_view_mode_first


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _order = "dashboard_sequence desc, sequence, name, id"

    dashboard_sequence = fields.Integer(
        string="Dashboard Position",
        default=0,
        help="If set, then this project will be displayed on the "
        "dashboard. A higher value indicats an higher priority."
    )

    kanban_description = fields.Char(compute="_compute_kanban_description")

    @api.multi
    def _compute_kanban_description(self):
        for rec in self:
            rec.kanban_description = rec.partner_shipping_id.display_name

    def action_open_all_tasks(self, view_domain=False, view_type=False):
        act = clean_action(self.env.ref("project.action_view_task").read()[0])

        project_ids = self.ids
        # We cannot rely on `self.ids` as it depends of loaded data in the
        # web client (Expand Group or Load More UI actions), so we get back
        # the original domain copied in context and we make our own search
        # view_domain = self.env.context.get('view_domain')
        if view_domain:
            project_ids = self.search(view_domain).ids

        act['context'] = {}
        act['domain'] = [('project_id', 'in', project_ids)]
        if view_type:
            act['views'] = set_view_mode_first(act['views'], view_type)

        return act

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        res = super(ProjectProject, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        if view_type == 'search':
            date_field = self.env.context.get('date_field', False)
            if date_field:
                res['arch'] = self._add_year_filters(res['arch'], date_field)
        return res

    @api.model
    def _add_year_filters(self, view_arch, date_field):
        doc = etree.XML(view_arch)
        for node in doc.xpath("//separator[last()]"):

            extra_nodes = [
                "<separator/>",
                """<filter string="{0}" name="filter_year_older" domain="[('{1}', '&lt;=', (datetime.date.today() - relativedelta(years=2)).strftime('%Y-12-31')),]"/>"""
                .format(_("More Older"), date_field),
                """<filter string="{0}" name="filter_year_previous" domain="[('{1}', '&gt;=', (datetime.date.today() - relativedelta(years=1)).strftime('%Y-01-01')),('{1}', '&lt;', datetime.date.today().strftime('%Y-01-01')),]"/>"""
                .format(_("Previous Year"), date_field),
                """<filter string="{0}" name="filter_year_current" domain="[('{1}', '&gt;=', datetime.date.today().strftime('%Y-01-01'))]"/>"""
                .format(_("Current Year"), date_field),
            ]

            for extra_node in extra_nodes:
                new_node = etree.XML(extra_node)
                node.addnext(new_node)

        return etree.tostring(doc, encoding='unicode')
