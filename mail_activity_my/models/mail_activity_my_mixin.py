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
            else:
                record.activity_my_state = False

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

    # yapf: disable
    def _read_progress_bar(self, domain, group_by, progress_bar):
        """ This method is a copy/paste of existing implementation for
            activity_state, except following:
            - `activity_state` replaced with `activity_my_state`
            - `_last_activity_state` replaced with `_last_activity_my_state`
            - `AND mail_activity.user_id = '{user}'` added to the WHERE join
            - `user=self._uid,` added to format params
        """
        group_by_fname = group_by.partition(':')[0]
        if not (progress_bar['field'] == 'activity_my_state' and self._fields[group_by_fname].store):
            return super()._read_progress_bar(domain, group_by, progress_bar)

        # optimization for 'activity_my_state'

        # explicitly check access rights, since we bypass the ORM
        self.check_access_rights('read')
        query = self._where_calc(domain)
        self._apply_ir_rules(query, 'read')
        gb = group_by.partition(':')[0]
        annotated_groupbys = [
            self._read_group_process_groupby(gb, query)
            for gb in [group_by, 'activity_my_state']
        ]
        groupby_dict = {gb['groupby']: gb for gb in annotated_groupbys}
        for gb in annotated_groupbys:
            if gb['field'] == 'activity_my_state':
                gb['qualified_field'] = '"_last_activity_my_state"."activity_my_state"'
        groupby_terms, orderby_terms = self._read_group_prepare('activity_my_state', [], annotated_groupbys, query)
        select_terms = [
            '%s as "%s"' % (gb['qualified_field'], gb['groupby'])
            for gb in annotated_groupbys
        ]
        from_clause, where_clause, where_params = query.get_sql()
        tz = self._context.get('tz') or self.env.user.tz or 'UTC'
        select_query = """
            SELECT 1 AS id, count(*) AS "__count", {fields}
            FROM {from_clause}
            JOIN (
                SELECT res_id,
                CASE
                    WHEN min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %s))::date) > 0 THEN 'planned'
                    WHEN min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %s))::date) < 0 THEN 'overdue'
                    WHEN min(date_deadline - (now() AT TIME ZONE COALESCE(res_partner.tz, %s))::date) = 0 THEN 'today'
                    ELSE null
                END AS activity_my_state
                FROM mail_activity
                JOIN res_users ON (res_users.id = mail_activity.user_id)
                JOIN res_partner ON (res_partner.id = res_users.partner_id)
                WHERE res_model = '{model}' AND mail_activity.user_id = '{user}'
                GROUP BY res_id
            ) AS "_last_activity_my_state" ON ("{table}".id = "_last_activity_my_state".res_id)
            WHERE {where_clause}
            GROUP BY {group_by}
        """.format(
            fields=', '.join(select_terms),
            from_clause=from_clause,
            model=self._name,
            user=self._uid,
            table=self._table,
            where_clause=where_clause or '1=1',
            group_by=', '.join(groupby_terms),
        )
        self.env.cr.execute(select_query, [tz] * 3 + where_params)
        fetched_data = self.env.cr.dictfetchall()
        self._read_group_resolve_many2one_fields(fetched_data, annotated_groupbys)
        data = [
            {key: self._read_group_prepare_data(key, val, groupby_dict)
             for key, val in row.items()}
            for row in fetched_data
        ]
        return [
            self._read_group_format_result(vals, annotated_groupbys, [group_by], domain)
            for vals in data
        ]
    # yapf: enable
