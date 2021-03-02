# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    autofill_from_analytic_line_id = fields.Many2one(
        'account.analytic.line',
        string="Auto-fill",
        help='Help to pre-fill timesheet using another entry',
    )

    @api.model
    def create(self, vals):
        if 'autofill_from_analytic_line_id' in vals:
            vals.pop('autofill_from_analytic_line_id')
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
        access_rights_uid=None
    ):
        """ Override _search instead of search to also override
            name_search order
        """
        order = self.env.context.get("autofill_search_order", order)
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid
        )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if self.env.context.get("autofill_name_search"):
            # Add line details to quickly identify its content
            autofill_fields = self.get_autofill_fields()
            autofill_fields.remove('name')
            result = []
            for item in names:
                rec = self.browse(item[0])[0]
                name = str(item[1])
                extra_name = []
                for fname in autofill_fields:
                    fvalue = rec[fname]
                    if hasattr(fvalue, 'display_name'):
                        val = fvalue.display_name or ''
                    else:
                        val = str(fvalue)
                    if val and val not in extra_name:
                        extra_name.append(val)
                name = '{}: {}'.format(' / '.join(extra_name), name)
                result.append((item[0], name))
            return result
        else:
            return names

    @api.model
    def get_autofill_fields(self):
        return [
            'name',
            'project_id',
            'task_id',
        ]

    @api.onchange('autofill_from_analytic_line_id')
    def onchange_autofill_from_analytic_line_id(self):
        """ Copy fields from selected autofill_from_analytic_line_id
        """
        if self.autofill_from_analytic_line_id:
            for fname in self.get_autofill_fields():
                fvalue = self.autofill_from_analytic_line_id[fname]
                setattr(self, fname, fvalue)
