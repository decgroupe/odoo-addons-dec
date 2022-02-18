# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from datetime import date, timedelta
from odoo import api, models, fields

import logging

_logger = logging.getLogger(__name__)


class MailActivityMyMixin(models.AbstractModel):
    _name = 'mail.activity.my.mixin'
    _description = 'My Activity Mixin'

    activity_my_ids = fields.One2many(
        comodel_name='mail.activity',
        inverse_name='res_id',
        string='My Activities',
        auto_join=True,
        groups="base.group_user",
        domain=lambda self: [
            ('res_model', '=', self._name),
            ('user_id', '=', self._uid),
        ]
    )
    activity_my_state = fields.Selection(
        selection=[
            ('overdue', 'Overdue'),
            ('today', 'Today'),
            ('planned', 'Planned'),
        ],
        string='My Activity State',
        compute='_compute_activity_my_state',
        groups="base.group_user",
        help='Status based on activities\n'
        'Overdue: Due date is already passed\n'
        'Today: Activity date is today\n'
        'Planned: Future activities.',
    )
    activity_my_user_id = fields.Many2one(
        comodel_name='res.users',
        string='My Next Activity User',
        compute='_compute_activity_my_user_id',
        # related='activity_my_ids.user_id',
        readonly=False,
        search='_search_activity_my_user_id',
        groups="base.group_user"
    )
    activity_my_type_id = fields.Many2one(
        comodel_name='mail.activity.type',
        string='My Next Activity Type',
        compute='_compute_activity_my_type_id',
        # related='activity_my_ids.activity_type_id',
        readonly=False,
        search='_search_activity_my_type_id',
        groups="base.group_user"
    )
    activity_my_date_deadline = fields.Date(
        'My Deadline',
        compute='_compute_activity_my_date_deadline',
        search='_search_activity_my_date_deadline',
        readonly=True,
        store=False,
        groups="base.group_user"
    )
    activity_my_summary = fields.Char(
        'My Next Activity Summary',
        compute='_compute_activity_my_summary',
        # related='activity_my_ids.summary',
        readonly=False,
        search='_search_activity_my_summary',
        groups="base.group_user",
    )

    activity_my_type_icon = fields.Char(
        string='My Activity Type Icon',
        compute='_compute_activity_my_type_icon',
        # related='activity_my_ids.icon',
    )

    @api.depends('activity_my_ids.state')
    def _compute_activity_my_state(self):
        for record in self:
            states = record.activity_my_ids.mapped('state')
            if 'overdue' in states:
                record.activity_my_state = 'overdue'
            elif 'today' in states:
                record.activity_my_state = 'today'
            elif 'planned' in states:
                record.activity_my_state = 'planned'

    @api.depends('activity_my_ids.user_id')
    def _compute_activity_my_user_id(self):
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_user_id = activity.user_id

    @api.depends('activity_my_ids.activity_type_id')
    def _compute_activity_my_type_id(self):
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_type_id = activity.activity_type_id

    @api.depends('activity_my_ids.date_deadline')
    def _compute_activity_my_date_deadline(self):
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_date_deadline = activity.date_deadline

    @api.depends('activity_my_ids.icon')
    def _compute_activity_my_type_icon(self):
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_type_icon = activity.icon

    @api.depends('activity_my_ids.summary')
    def _compute_activity_my_summary(self):
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_summary = activity.summary

    def _search_activity_my_date_deadline(self, operator, operand):
        if operator == '=' and not operand:
            return [('activity_my_ids', '=', False)]
        return [('activity_my_ids.date_deadline', operator, operand)]

    @api.model
    def _search_activity_my_user_id(self, operator, operand):
        return [('activity_my_ids.user_id', operator, operand)]

    @api.model
    def _search_activity_my_type_id(self, operator, operand):
        return [('activity_my_ids.activity_type_id', operator, operand)]

    @api.model
    def _search_activity_my_summary(self, operator, operand):
        return [('activity_my_ids.summary', operator, operand)]

    def action_snooze(self):
        self.ensure_one()
        today = date.today()
        my_next_activity = self.activity_my_ids[:1]
        if my_next_activity:
            delta = timedelta(days=7)
            if my_next_activity.date_deadline < today:
                date_deadline = today + delta
            else:
                date_deadline = my_next_activity.date_deadline + delta
            my_next_activity.write({'date_deadline': date_deadline})
        return True
