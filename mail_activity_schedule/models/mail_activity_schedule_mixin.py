# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, fields, models
from odoo.exceptions import UserError


class MailActivityScheduleMixin(models.AbstractModel):
    _name = "mail.activity.schedule.mixin"
    _description = "Activity Schedule Mixin"

    scheduling_activity_id = fields.Many2one(
        comodel_name="mail.activity",
        string="Scheduling Activity",
    )
    schedulable = fields.Boolean(
        string="Schedulable",
        compute="_compute_schedulable",
        help="A scheduling activity will be automatically created and synced "
        "while schedulable is set",
        store=True,
    )

    @api.model
    def create(self, vals):
        rec = super(MailActivityScheduleMixin, self).create(vals)
        if rec.schedulable:
            rec._ensure_scheduling_activity()
            rec._sync_with_scheduling_activity(vals)
        return rec

    def write(self, vals):
        res = super().write(vals)
        if res:
            self_schedulable = self.filtered("schedulable")
            if self_schedulable:
                self_schedulable._ensure_scheduling_activity()
                self_schedulable._sync_with_scheduling_activity(vals)
            else:
                self_scheduled = self.filtered("scheduling_activity_id")
                if self_scheduled:
                    self_scheduled._close_scheduling_activity()

        return res

    def _get_scheduling_activity_deadline(self):
        self.ensure_one()
        res = False
        date_fields = self._get_schedule_date_fields()
        if not res:
            if date_fields.get("deadline"):
                res = self[date_fields["deadline"]]
        if not res:
            # If no deadline is  set then use the stop date as deadline
            if date_fields.get("stop"):
                res = self[date_fields["stop"]]
        if not res:
            # If no stop date is set then use the start date as deadline
            if date_fields.get("start"):
                res = self[date_fields["start"]]
        if not res:
            # Finally, if no date at all is set, then use the current day
            res = fields.Date.context_today(self)
        return res

    def _prepare_scheduling_activity_data(self):
        self.ensure_one()
        act_type = self.env.ref("mail_activity_schedule.mail_activity_schedule")
        return {
            "activity_type_id": act_type.id,
            "user_id": self.user_id.id,
            "automated": True,
        }

    def _ensure_scheduling_activity(self):
        if "mail.activity.mixin" not in self._inherit_module:
            return
        for rec in self:
            if not rec.schedulable:
                raise UserError("You cannot ensure a scheduling activity")

            if not rec.scheduling_activity_id:
                activity_data = rec._prepare_scheduling_activity_data()
                if activity_data:
                    rec.scheduling_activity_id = rec.activity_schedule(
                        "", rec._get_scheduling_activity_deadline(), **activity_data
                    )
                    rec._sync_with_scheduling_activity(vals=False)

    def _sync_with_scheduling_activity(self, vals=False):
        if "mail.activity.mixin" not in self._inherit_module:
            return
        for rec in self.filtered("scheduling_activity_id").with_context(
            syncing_mail_activity=True
        ):
            context_name = "syncing_" + rec._name.replace(".", "_")
            if not rec.env.context.get(context_name, False):
                data = {}
                date_fields = rec._get_schedule_date_fields()
                if not vals or date_fields["start"] in vals:
                    data["date_start"] = rec[date_fields["start"]]
                if not vals or date_fields["stop"] in vals:
                    data["date_stop"] = rec[date_fields["stop"]]
                if not vals or date_fields["deadline"] in vals:
                    data["date_deadline"] = rec._get_scheduling_activity_deadline()
                if data:
                    rec.scheduling_activity_id.write(data)

    def _get_schedule_date_fields(self):
        return {
            "start": False,
            "stop": False,
            "deadline": False,
        }

    def _compute_schedulable(self):
        for rec in self:
            rec.schedulable = rec._is_schedulable()

    def _is_schedulable(self):
        self.ensure_one()
        return True

    def _close_scheduling_activity(self):
        for rec in self:
            rec.scheduling_activity_id.action_done()
            rec.scheduling_activity_id = False
