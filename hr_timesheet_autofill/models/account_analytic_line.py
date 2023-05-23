# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

import psycopg2

from odoo import SUPERUSER_ID, api, fields, models, registry
from odoo.addons.tools_miscellaneous.tools.bench import Bench
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    autofill_from_analytic_line_id = fields.Many2one(
        "account.analytic.line",
        string="Auto-fill",
        help="Help to pre-fill timesheet using another entry",
    )

    @api.model
    def create(self, vals):
        if "autofill_from_analytic_line_id" in vals:
            vals.pop("autofill_from_analytic_line_id")
        res = super().create(vals)
        return res

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """Override _search instead of search to also override
        name_search order
        """
        order = self.env.context.get("autofill_search_order", order)
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        def log_query(msg, id=False):
            # Use a new cursor to avoid rollback that could be caused by
            # an upper method
            try:
                db_registry = registry(self._cr.dbname)
                with db_registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    path = "autofill_name_search by %s" % (self.env.user.name)
                    data = {
                        "name": self._name,
                        "type": "server",
                        "dbname": self._cr.dbname,
                        "level": "DEBUG",
                        "message": msg,
                        "path": path,
                        "func": "name_search",
                        "line": 1,
                    }
                    if id:
                        env["ir.logging"].browse(id).sudo().write(data)
                        return id
                    else:
                        data["func"] += " in progress ..."
                        ir_logging = env["ir.logging"].sudo().create(data)
                        return ir_logging.id
            except psycopg2.Error:
                pass

        # Make a search for all autofill fields and clear default name arg to
        # avoid `expression.AND` collision
        if self.env.context.get("autofill_name_search"):
            bench = Bench().start()
            # To avoid long-waiting query, we first search for all lines owned
            # by this user. It has better performance than making a long AND
            # query including user_id
            domain = [
                ("user_id", "=", self.env.uid),
                ("project_id", "!=", False),
            ]
            owned_ids = self.env["account.analytic.line"].search(domain)
            args.append(("id", "in", owned_ids.ids))
            # Execute normal search
            autofill_fields = self.get_autofill_fields()
            if len(name) > 2:
                extra_args = []
                for value in name.split():
                    if len(value) > 2:
                        value_args = []
                        for fname in autofill_fields:
                            value_args = expression.OR(
                                [value_args, [(fname, "ilike", value)]]
                            )
                        extra_args = expression.AND([extra_args, value_args])
                if extra_args:
                    args = expression.AND([args, extra_args])
                    name = ""
            if _logger.isEnabledFor(logging.DEBUG):
                log_id = log_query("Autofill query: {} in progress".format(args))

        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )

        if _logger.isEnabledFor(logging.DEBUG):
            if self.env.context.get("autofill_name_search"):
                duration = bench.stop().duration()
                log_query("Autofill query: {} in {}s".format(args, duration), log_id)

        if self.env.context.get("autofill_name_search"):
            autofill_fields = self.get_autofill_fields()
            # Add line details to quickly identify its content
            autofill_fields.remove("name")
            result = []
            for item in names:
                rec = self.browse(item[0])[0]
                name = str(item[1])
                extra_name = []
                for fname in autofill_fields:
                    fvalue = rec[fname]
                    if hasattr(fvalue, "display_name"):
                        val = fvalue.display_name or ""
                    elif fvalue:
                        val = str(fvalue)
                    else:
                        val = False
                    if val and val not in extra_name:
                        extra_name.append(val)
                name = "{}: {}".format(" / ".join(extra_name), name)
                result.append((item[0], name))
            return result
        else:
            return names

    @api.model
    def get_autofill_fields(self):
        return [
            "name",
            "project_id",
            "task_id",
        ]

    @api.onchange("autofill_from_analytic_line_id")
    def onchange_autofill_from_analytic_line_id(self):
        """Copy fields from selected autofill_from_analytic_line_id"""
        if self.autofill_from_analytic_line_id:
            for fname in self.get_autofill_fields():
                fvalue = self.autofill_from_analytic_line_id[fname]
                setattr(self, fname, fvalue)
