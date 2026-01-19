# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import api, fields, models

SEARCH_SEPARATOR = "→"

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    is_contract = fields.Boolean(
        string="Is for a contract",
        compute="_compute_from_type",
        store=True,
    )
    is_time_tracking = fields.Boolean(
        string="Is for time tracking",
        compute="_compute_from_type",
        store=True,
    )

    @api.depends("type_id")
    def _compute_from_type(self):
        self.is_contract = False
        self.is_time_tracking = False
        if self.env.context.get("module") == "project_identification":
            return
        contract_type = self.env.ref("project_identification.contract_type")
        time_tracking_type = self.env.ref("project_identification.time_tracking_type")
        for rec in self:
            rec.is_contract = rec.type_id == contract_type
            rec.is_time_tracking = rec.type_id == time_tracking_type

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # it is important to clean the name from identification to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(Project, self.with_context(name_search=True)).name_search(
            name=self._clean_name_identification(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    @api.depends("name", "type_id", "type_id.complete_name")
    def _compute_display_name(self):
        """Custom naming with type to quickly identify a project"""
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            for rec in self:
                name = " ".join(rec._get_name_identifications(rec.display_name))
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

    def _get_name_identifications(self, base_name=None):
        self.ensure_one()
        res = [base_name or self.display_name]
        if self.type_id:
            res.append(self.type_id.complete_name)
        if len(res) > 1:
            res.insert(1, SEARCH_SEPARATOR)
        return res

    def _clean_name_identification(self, name):
        _logger.info("Cleaning name identification: <= %s", name)
        # if not name:
        #     # print traceback in logs to understand when this happens
        #     raise ValueError(
        #         f"Received falsy name '{name}' for cleaning, this should not happen,"
        #         " check the stacktrace to understand why"
        #     )

        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0].strip()
        _logger.info("Cleaning name identification: => %s", name)
        return name
