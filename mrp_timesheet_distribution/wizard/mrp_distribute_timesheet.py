# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import logging
from datetime import datetime, timedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MrpDistributeTimesheetLine(models.TransientModel):
    _name = 'mrp.distribute.timesheet.line'
    _description = 'Represents a sample of the distribution'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    production_id = fields.Many2one(
        'mrp.production',
        string='Production',
    )
    start_time = fields.Datetime()
    end_time = fields.Datetime()

    def _prepare_analytic_line(self, name):
        diff = self.end_time - self.start_time
        hours = diff.total_seconds() / 3600
        vals = {
            'name': name,
            'project_id': self.project_id.id,
            'production_id': self.production_id.id,
            'date_time': self.start_time,
            'unit_amount': hours,
        }
        return vals


class MrpDistributeTimesheet(models.TransientModel):
    _name = 'mrp.distribute.timesheet'
    _description = 'Distribute working time along multiple production orders'

    @api.model
    def _default_date_time(self):
        def ceil_dt(dt, delta):
            return dt + (datetime.min - dt) % delta

        return ceil_dt(fields.Datetime.now(), timedelta(minutes=-15))

    @api.model
    def _default_reason(self):
        return self.env.ref('mrp_timesheet_distribution.layout_and_wiring')

    production_ids = fields.Many2many(
        'mrp.production',
        string='Production Orders',
        readonly=True,
    )
    reason_id = fields.Many2one(
        'mrp.distribute.timesheet.reason',
        string='Reason',
        required=True,
        default=_default_reason
    )
    custom_reason = fields.Char(string='Other Reason')
    date_time = fields.Datetime(
        default=_default_date_time,
        required=True,
    )
    unit_amount = fields.Float(
        'Quantity',
        default=0.0,
        required=True,
    )
    timesheet_line_ids = fields.Many2many(
        'mrp.distribute.timesheet.line',
        string='Timesheet Lines',
        compute="_compute_timesheet_line_ids",
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if active_model == 'mrp.production' and active_ids:
            production_ids = self.env['mrp.production'].browse(active_ids)
            rec.update({'production_ids': production_ids.ids})
        return rec

    @api.multi
    def action_reopen(self):
        return self._reopen()

    @api.multi
    def _reopen(self, id=False):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': id or self.id,
            'res_model': self._name,
            'target': 'new',
            'context': {
                'default_model': self._name,
            },
        }

    @api.multi
    def action_distribute(self):
        self._do_distribute()

    @api.multi
    def action_distribute_continue(self):
        self._do_distribute()
        mrp_distribute_timesheet_id = self.create(
            {
                "date_time": self.timesheet_line_ids[-1].end_time,
                "reason_id": self.reason_id.id,
                "production_ids": [(6, 0, self.production_ids.ids)],
            }
        )
        return self._reopen(mrp_distribute_timesheet_id.id)

    @api.depends('date_time', 'unit_amount')
    def _compute_timesheet_line_ids(self):
        self.timesheet_line_ids.unlink()
        if self.production_ids and self.date_time and self.unit_amount:
            start = self.date_time
            end = self.date_time + timedelta(hours=self.unit_amount)
            diff = (end - start) / len(self.production_ids)
            i = 0
            line_ids = self.env['mrp.distribute.timesheet.line']
            for production_id in self.production_ids:
                vals = {
                    'start_time': i * diff + start,
                    'end_time': (i + 1) * diff + start,
                    'project_id': production_id.project_id.id,
                    'production_id': production_id.id,
                }
                line_ids += self.env['mrp.distribute.timesheet.line'].create(
                    vals
                )
                i += 1
            self.timesheet_line_ids = line_ids

    def _get_or_create_task(self, project_id, name):
        task_id = self.env['project.task'].search(
            [('project_id', '=', project_id.id), ('name', '=', name)], limit=1
        )
        if not task_id:
            vals = {
                'project_id': project_id.id,
                'name': name,
            }
            task_id = self.env['project.task'].create(vals)
        return task_id

    def _do_distribute(self):
        if not self.timesheet_line_ids:
            raise ValidationError(
                _('The number of timesheet lines cannot be 0.')
            )

        for line_id in self.timesheet_line_ids:
            name = self.reason_id.name
            if self.reason_id == self.env.ref(
                'mrp_timesheet_distribution.other'
            ):
                name = self.custom_reason

            vals_line = line_id._prepare_analytic_line(name)
            if not 'task_id' in vals_line:
                vals_line['task_id'] = self._get_or_create_task(
                    line_id.project_id, name
                ).id

            self.env['account.analytic.line'].create(vals_line)
        # previous_product_ids = self.replacement_ids.mapped(
        #     'previous_product_id'
        # )
        # boms_data = self.env['mrp.bom.line'].read_group(
        #     [
        #         ('product_id', 'in', previous_product_ids.ids),
        #         ('bom_id', 'in', self.bom_ids.ids),
        #     ], ['bom_id'], ['bom_id']
        # )
        # bom_to_process_ids = [x['bom_id'][0] for x in boms_data]

        # for bom_id in self.env['mrp.bom'].browse(bom_to_process_ids):
        #     _logger.info('Processing BoM %s', bom_id.code)
        #     values = {'lines': {}}
        #     replace_count = 0
        #     for bom_line in bom_id.bom_line_ids.filtered(
        #         lambda x: x.product_id in previous_product_ids
        #     ):
        #         for replacement_id in self.replacement_ids:
        #             if bom_line.product_id == replacement_id.previous_product_id:
        #                 values['lines'][bom_line] = {
        #                     'before': bom_line.product_id,
        #                     'after': replacement_id.new_product_id,
        #                 }
        #                 bom_line.product_id = replacement_id.new_product_id
        #                 replace_count += 1
        #                 break

        #     if replace_count > 0:
        #         bom_id.message_post_with_view(
        #             'mrp_bom_replace_components.track_bom_line_template',
        #             values=values,
        #             subtype_id=self.env.ref('mail.mt_note').id
        #         )
