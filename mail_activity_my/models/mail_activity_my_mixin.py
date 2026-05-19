# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import logging
from datetime import date, datetime, timedelta

import pytz

from odoo import api, fields, models
from odoo.tools import SQL

_logger = logging.getLogger(__name__)


class MailActivityMyMixin(models.AbstractModel):
    _name = "mail.activity.my.mixin"
    _description = "My Activity Mixin"

    activity_my_ids = fields.One2many(
        comodel_name="mail.activity",
        inverse_name="res_id",
        string="My Activities",
        auto_join=True,
        groups="base.group_user",
        domain=lambda self: [
            ("res_model", "=", self._name),
            ("user_id", "=", self._uid),
        ],
    )
    activity_my_state = fields.Selection(
        selection=[
            ("overdue", "Overdue"),
            ("today", "Today"),
            ("planned", "Planned"),
        ],
        string="My Activity State",
        compute="_compute_activity_my_state",
        groups="base.group_user",
        help="Status based on activities\n"
        "Overdue: Due date is already passed\n"
        "Today: Activity date is today\n"
        "Planned: Future activities.",
    )
    activity_my_user_id = fields.Many2one(
        comodel_name="res.users",
        string="My Next Activity User",
        compute="_compute_activity_my_user_id",
        # related='activity_my_ids.user_id',
        readonly=False,
        search="_search_activity_my_user_id",
        groups="base.group_user",
    )
    activity_my_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        string="My Next Activity Type",
        compute="_compute_activity_my_type_id",
        # related='activity_my_ids.activity_type_id',
        readonly=False,
        search="_search_activity_my_type_id",
        groups="base.group_user",
    )
    activity_my_date_deadline = fields.Date(
        "My Deadline",
        compute="_compute_activity_my_date_deadline",
        search="_search_activity_my_date_deadline",
        readonly=True,
        store=False,
        groups="base.group_user",
    )
    activity_my_summary = fields.Char(
        "My Next Activity Summary",
        compute="_compute_activity_my_summary",
        # related='activity_my_ids.summary',
        readonly=False,
        search="_search_activity_my_summary",
        groups="base.group_user",
    )

    activity_my_type_icon = fields.Char(
        string="My Activity Type Icon",
        compute="_compute_activity_my_type_icon",
        # related='activity_my_ids.icon',
    )

    @api.depends("activity_my_ids.state")
    def _compute_activity_my_state(self):
        """Compute activity_my_state based on the current user's activities."""
        for record in self:
            states = record.activity_my_ids.mapped("state")
            if "overdue" in states:
                record.activity_my_state = "overdue"
            elif "today" in states:
                record.activity_my_state = "today"
            elif "planned" in states:
                record.activity_my_state = "planned"
            else:
                record.activity_my_state = False

    @api.depends("activity_my_ids.user_id")
    def _compute_activity_my_user_id(self):
        """Compute the user id from the first of the current user's activities."""
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_user_id = activity.user_id

    @api.depends("activity_my_ids.activity_type_id")
    def _compute_activity_my_type_id(self):
        """Compute the activity type from the first of the current user's activities."""
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_type_id = activity.activity_type_id

    @api.depends("activity_my_ids.date_deadline")
    def _compute_activity_my_date_deadline(self):
        """Compute the deadline from the first of the current user's activities."""
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_date_deadline = activity.date_deadline

    @api.depends("activity_my_ids.icon")
    def _compute_activity_my_type_icon(self):
        """Compute the activity type icon from the first of the current user's
        activities."""
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_type_icon = activity.icon

    @api.depends("activity_my_ids.summary")
    def _compute_activity_my_summary(self):
        """Compute the summary from the first of the current user's activities."""
        for record in self:
            activity = record.activity_my_ids[:1]
            record.activity_my_summary = activity.summary

    def _search_activity_my_date_deadline(self, operator, operand):
        """Search on activity_my_date_deadline field."""
        if operator == "=" and not operand:
            return [("activity_my_ids", "=", False)]
        return [("activity_my_ids.date_deadline", operator, operand)]

    @api.model
    def _search_activity_my_user_id(self, operator, operand):
        """Search on activity_my_user_id field."""
        return [("activity_my_ids.user_id", operator, operand)]

    @api.model
    def _search_activity_my_type_id(self, operator, operand):
        """Search on activity_my_type_id field."""
        return [("activity_my_ids.activity_type_id", operator, operand)]

    @api.model
    def _search_activity_my_summary(self, operator, operand):
        """Search on activity_my_summary field."""
        return [("activity_my_ids.summary", operator, operand)]

    def action_snooze(self):
        """Snooze the current user's next activity by 7 days."""
        self.ensure_one()
        today = date.today()
        my_next_activity = self.activity_my_ids[:1]
        if my_next_activity:
            delta = timedelta(days=7)
            if my_next_activity.date_deadline < today:
                date_deadline = today + delta
            else:
                date_deadline = my_next_activity.date_deadline + delta
            my_next_activity.write({"date_deadline": date_deadline})
        return True

    def _read_group_groupby(self, groupby_spec, query):
        """Override to support groupby on activity_my_state with user filtering.

        This is an adaptation of mail.activity.mixin._read_group_groupby for
        the user-specific activity state. It adds a WHERE clause to filter
        activities belonging to the current user only.
        """
        if groupby_spec != "activity_my_state":
            return super()._read_group_groupby(groupby_spec, query)
        self.check_field_access_rights("read", ["activity_my_state"])
        self.env["mail.activity"].flush_model(
            ["res_model", "res_id", "user_id", "date_deadline"]
        )
        self.env["res.users"].flush_model(["partner_id"])
        self.env["res.partner"].flush_model(["tz"])
        tz = "UTC"
        if self.env.context.get("tz") in pytz.all_timezones_set:
            tz = self.env.context["tz"]
        sql_join = SQL(
            """
            (SELECT res_id,
                CASE
                    WHEN min(EXTRACT(day from (
                        mail_activity.date_deadline - DATE_TRUNC(
                            'day', %(today_utc)s AT TIME ZONE
                            COALESCE(mail_activity.user_tz, %(tz)s)
                        )))) > 0 THEN 'planned'
                    WHEN min(EXTRACT(day from (
                        mail_activity.date_deadline - DATE_TRUNC(
                            'day', %(today_utc)s AT TIME ZONE
                            COALESCE(mail_activity.user_tz, %(tz)s)
                        )))) < 0 THEN 'overdue'
                    WHEN min(EXTRACT(day from (
                        mail_activity.date_deadline - DATE_TRUNC(
                            'day', %(today_utc)s AT TIME ZONE
                            COALESCE(mail_activity.user_tz, %(tz)s)
                        )))) = 0 THEN 'today'
                    ELSE null
                END AS activity_my_state
            FROM mail_activity
            WHERE res_model = %(res_model)s
                AND mail_activity.active = true
                AND mail_activity.user_id = %(user_id)s
            GROUP BY res_id)
            """,
            res_model=self._name,
            today_utc=pytz.utc.localize(datetime.utcnow()),
            tz=tz,
            user_id=self._uid,
        )
        alias = query.left_join(
            self._table, "id", sql_join, "res_id", "last_activity_my_state"
        )
        return SQL.identifier(alias, "activity_my_state")
