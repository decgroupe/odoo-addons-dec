# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models

SEARCH_SEPARATOR = "→"


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_type_id = fields.Many2one(
        comodel_name="project.type",
        string="Project Type",
        related="project_id.type_id",
        store=True,
    )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # it is important to clean the name from identification to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(ProjectTask, self.with_context(name_search=True)).name_search(
            name=self._clean_name_identification(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    @api.depends(
        "name",
        "stage_id",
        "project_id",
        "project_id.type_id",
        "project_id.type_id.name",
    )
    def _compute_display_name(self):
        """Custom naming with multiple identification parts to quickly
        identify a task
        """
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            for rec in self:
                name = " ".join(rec._get_name_identifications(rec.display_name))
                if rec.stage_id and not rec.stage_id.name[0].isalpha():
                    symbol = rec.stage_id.name[0]
                    name = f"{symbol} {name}"
                rec.display_name = name
        return res

    def _search_display_name(self, operator, value):
        if self.env.context.get("name_search"):
            # this steps is only a fallback in case of a direct call, the real cleaning
            # is done in name_search, but we want to be sure that the search is clean
            # in any case
            value = self._clean_name_identification(value)
        res = super()._search_display_name(operator, value)
        return res

    def _get_name_identifications(self, base_name):
        self.ensure_one()
        res = [base_name]
        # Add project to quickly identify a task
        project_id = self.project_id
        if project_id:
            project_name = project_id.name
            if project_id.type_id and not project_id.type_id.display_name[0].isalpha():
                symbol = project_id.type_id.display_name[0]
                project_name = f"{symbol} {project_name}"
                res.append(project_name)
        if len(res) > 1:
            res.insert(1, SEARCH_SEPARATOR)
        return res

    def _clean_name_identification(self, name):
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0].strip()
            # Remove 'stage' symbol
            if name and not name[0].isalpha():
                name = name[1:].strip()
        return name
