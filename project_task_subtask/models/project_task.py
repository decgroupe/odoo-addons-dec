# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2023

from odoo import fields, models
from odoo.tools import html_escape as escape
from odoo.tools.translate import _

from .project_task_subtask import SUBTASK_STATES


class Task(models.Model):
    _inherit = "project.task"

    subtask_ids = fields.One2many(
        comodel_name="project.task.subtask",
        inverse_name="task_id",
        string="Subtask",
    )
    default_user = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_default_user",
    )
    user_active_subtask_ids = fields.One2many(
        comodel_name="project.task.subtask",
        compute="_compute_user_subtask_ids",
        string="My sub-tasks (active)",
    )
    user_done_subtask_ids = fields.One2many(
        comodel_name="project.task.subtask",
        compute="_compute_user_subtask_ids",
        string="My sub-tasks (done)",
    )
    user_todo_subtask_ids = fields.One2many(
        comodel_name="project.task.subtask",
        compute="_compute_user_subtask_ids",
        string="My sub-tasks (todo)",
    )
    user_waiting_subtask_ids = fields.One2many(
        comodel_name="project.task.subtask",
        compute="_compute_user_subtask_ids",
        string="My sub-tasks (waiting)",
    )
    user_done_subtask_progress = fields.Integer(
        string="% Done",
        compute="_compute_user_subtask_ids",
    )
    user_todo_subtask_progress = fields.Integer(
        string="% Todo",
        compute="_compute_user_subtask_ids",
    )
    user_waiting_subtask_progress = fields.Integer(
        string="% Waiting",
        compute="_compute_user_subtask_ids",
    )
    kanban_subtasks_progress_bar = fields.Text(
        compute="_compute_kanban_subtasks_user_progress",
    )
    kanban_subtasks_progress_list = fields.Text(
        compute="_compute_kanban_subtasks_user_progress",
    )

    def _compute_default_user(self):
        self.default_user = False
        for record in self:
            if self.env.user != record.user_id and self.env.user != record.create_uid:
                record.default_user = record.user_id
            else:
                if self.env.user != record.user_id:
                    record.default_user = record.user_id
                elif self.env.user != record.create_uid:
                    record.default_user = record.create_uid
                elif (
                    self.env.user == record.create_uid
                    and self.env.user == record.user_id
                ):
                    record.default_user = self.env.user

    def _li_task(self, name, subtask_ids):
        if not subtask_ids:
            return ""
        counter = escape(str(len(subtask_ids)))
        return (
            '<li class="count_progress_item">{}: <span class="number">{}</span></li>'
        ).format(name, counter)

    def _compute_kanban_subtasks_user_progress(self):
        self.kanban_subtasks_progress_bar = ""
        self.kanban_subtasks_progress_list = ""
        for rec in self:
            # Progress Bar
            bar = ""
            if rec.user_active_subtask_ids:
                header = _("Your Checklist:")
                bar = """
                <div class="progress_info">
                    {0}
                </div>
                <div class="progress_container">
                    <div class="o_kanban_counter_progress progress task_progress_bar">
                        <div class ="progress-bar bg-success-full" style="width: {1}%;"/>
                        <div class ="progress-bar bg-warning-full" style="width: {2}%;"/>
                    </div>
                    <div class="task_completion"> {1}% </div>
                </div>
                """.format(
                    header,
                    rec.user_done_subtask_progress,
                    rec.user_waiting_subtask_progress,
                )
            rec.kanban_subtasks_progress_bar = (
                '<div class="task_progress">{0}</div>'.format(bar)
            )
            # Progress List
            lis = ""
            if rec.user_done_subtask_ids:
                lis += rec._li_task(_("Done"), rec.user_done_subtask_ids)
            if rec.user_waiting_subtask_ids:
                lis += rec._li_task(_("Waiting"), rec.user_waiting_subtask_ids)
            if rec.user_todo_subtask_ids:
                lis += rec._li_task(_("Todo"), rec.user_todo_subtask_ids)
            rec.kanban_subtasks_progress_list = (
                '<div class="kanban_subtasks"><ul>{}</ul></div>'.format(lis)
            )

    def _compute_user_subtask_ids(self):
        for rec in self:
            rec.user_active_subtask_ids = rec.subtask_ids.filtered(
                lambda x: x.user_id.id == rec.env.user.id and x.state != "cancelled"
            )
            if not rec.user_active_subtask_ids:
                # Tasks
                rec.user_done_subtask_ids = False
                rec.user_todo_subtask_ids = False
                rec.user_waiting_subtask_ids = False
                # Count
                rec.user_done_subtask_progress = 100
                rec.user_todo_subtask_progress = 100
                rec.user_waiting_subtask_progress = 100
            else:
                # Tasks
                rec.user_done_subtask_ids = rec.user_active_subtask_ids.filtered(
                    lambda x: x.state == "done"
                )
                rec.user_todo_subtask_ids = rec.user_active_subtask_ids.filtered(
                    lambda x: x.state == "todo"
                )
                rec.user_waiting_subtask_ids = rec.user_active_subtask_ids.filtered(
                    lambda x: x.state == "waiting"
                )
                # Count
                active_count = len(rec.user_active_subtask_ids)
                rec.user_done_subtask_progress = (
                    len(rec.user_done_subtask_ids) / active_count
                ) * 100
                rec.user_todo_subtask_progress = (
                    len(rec.user_todo_subtask_ids) / active_count
                ) * 100
                rec.user_waiting_subtask_progress = (
                    len(rec.user_waiting_subtask_ids) / active_count
                ) * 100

    def send_subtask_email(
        self,
        subtask_name,
        subtask_state,
        subtask_reviewer_id,
        subtask_user_id,
        old_name=None,
    ):
        for r in self:
            body = ""
            reviewer = self.env["res.users"].browse(subtask_reviewer_id)
            user = self.env["res.users"].browse(subtask_user_id)
            state = _(SUBTASK_STATES[subtask_state])
            if subtask_state == "done":
                state = '<span style="color:#080">' + state + "</span>"
            if subtask_state == "todo":
                state = '<span style="color:#A00">' + state + "</span>"
            if subtask_state == "cancelled":
                state = '<span style="color:#777">' + state + "</span>"
            if subtask_state == "waiting":
                state = '<span style="color:#b818ce">' + state + "</span>"
            partner_ids = []
            subtype_xmlid = "project_task_subtask.subtasks_subtype"
            if user == self.env.user and reviewer == self.env.user:
                body = "<p>" + "<strong>" + state + "</strong>: " + escape(subtask_name)
                subtype_xmlid = False
            elif self.env.user == reviewer:
                body = (
                    "<p>"
                    + escape(user.name)
                    + ", <br><strong>"
                    + state
                    + "</strong>: "
                    + escape(subtask_name)
                )
                partner_ids = [user.partner_id.id]
            elif self.env.user == user:
                msg = _("I updated checklist item assigned to me")
                body = (
                    "<p>"
                    + escape(reviewer.name)
                    + ', <em style="color:#999">'
                    + msg
                    + ":</em> <br><strong>"
                    + state
                    + "</strong>: "
                    + escape(subtask_name)
                )
                partner_ids = [reviewer.partner_id.id]
            else:
                msg = _("I updated checklist item, now its assigned to")
                body = (
                    "<p>"
                    + escape(user.name)
                    + ", "
                    + escape(reviewer.name)
                    + ', <em style="color:#999">'
                    + msg
                    + " "
                    + escape(user.name)
                    + ": </em> <br><strong>"
                    + state
                    + "</strong>: "
                    + escape(subtask_name)
                )
                partner_ids = [user.partner_id.id, reviewer.partner_id.id]
            if old_name:
                msg = _("Updated from")
                body = (
                    body
                    + '<br><em style="color:#999">'
                    + msg
                    + "</em><br><strong>"
                    + state
                    + "</strong>: "
                    + escape(old_name)
                    + "</p>"
                )
            else:
                body = body + "</p>"
            r.message_post(
                message_type="comment",
                subtype_xmlid=subtype_xmlid,
                body=body,
                partner_ids=partner_ids,
            )

    def copy(self, default=None):
        task = super(Task, self).copy(default)
        for subtask in self.subtask_ids:
            subtask.copy({"task_id": task.id, "state": subtask.state})
        return task
