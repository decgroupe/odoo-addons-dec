# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 manawi <https://github.com/manawi>
# Copyright 2017-2018 Karamov Ilmir <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018 iledarn <https://github.com/iledarn>
# Copyright 2017 Nicolas JEUDY <https://github.com/njeudy>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import Command, api, fields, models
from odoo.exceptions import UserError

SUBTASK_STATES = {
    "done": "Done",
    "todo": "To-Do",
    "waiting": "Waiting",
    "cancelled": "Cancelled",
}


class ProjectTaskSubtask(models.Model):
    _name = "project.task.subtask"
    _inherit = ["mail.activity.mixin"]

    state = fields.Selection(
        selection=[(k, v) for k, v in list(SUBTASK_STATES.items())],
        string="Status",
        required=True,
        copy=False,
        default="todo",
    )
    name = fields.Char(
        required=True,
        string="Description",
    )
    note = fields.Char(
        string="Note",
        help="Add details or comments",
    )
    reviewer_id = fields.Many2one(
        comodel_name="res.users",
        string="Created by",
        readonly=True,
        default=lambda self: self.env.user,
    )
    project_id = fields.Many2one(
        comodel_name="project.project",
        related="task_id.project_id",
        store=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        required=True,
    )
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        ondelete="cascade",
        required=True,
        index=True,
    )
    task_state = fields.Char(
        string="Task state",
        related="task_id.stage_id.name",
        readonly=True,
    )
    hide_button = fields.Boolean(
        compute="_compute_hide_button",
    )
    recolor = fields.Boolean(
        compute="_compute_recolor",
    )
    deadline = fields.Datetime(
        string="Deadline",
    )

    @api.depends_context("uid")
    def _compute_recolor(self):
        """Compute if the row should be highlighted for the current user."""
        self.recolor = False
        for record in self:
            if self.env.user == record.user_id and record.state == "todo":
                record.recolor = True

    @api.depends_context("uid")
    def _compute_hide_button(self):
        """Compute if action buttons should be hidden for the current user."""
        self.hide_button = False
        for record in self:
            if (
                self.env.user not in [record.reviewer_id, record.user_id]
                and not self.env.user._is_admin()
            ):
                record.hide_button = True

    def _compute_reviewer_id(self):
        """Compute the reviewer from the record creator."""
        self.reviewer_id = False
        for record in self:
            record.reviewer_id = record.create_uid

    def write(self, vals):
        """Override write to send notification emails on state/name/user changes."""
        old_names = dict(
            list(zip(self.mapped("id"), self.mapped("name"), strict=False))
        )
        result = super().write(vals)
        for r in self:
            if vals.get("state"):
                r.task_id.send_subtask_email(
                    r.name, r.state, r.reviewer_id.id, r.user_id.id
                )
                if not (
                    self.env.user == r.reviewer_id
                    or self.env.user == r.user_id
                    or self.env.user._is_admin()
                ):
                    raise UserError(
                        self.env._(
                            "Only users related to that subtask can change the state."
                        )
                    )
            if vals.get("name"):
                r.task_id.send_subtask_email(
                    r.name,
                    r.state,
                    r.reviewer_id.id,
                    r.user_id.id,
                    old_name=old_names[r.id],
                )
                if not (
                    self.env.user == r.reviewer_id
                    or self.env.user == r.user_id
                    or self.env.user._is_admin()
                ):
                    raise UserError(
                        self.env._(
                            "Only users related to that subtask can change the name."
                        )
                    )
            if vals.get("user_id"):
                r.task_id.send_subtask_email(
                    r.name, r.state, r.reviewer_id.id, r.user_id.id
                )
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Create subtask records and send notification emails after creation."""
        records = super().create(vals_list)
        for record in records:
            record.task_id.send_subtask_email(
                record.name,
                record.state,
                record.reviewer_id.id,
                record.user_id.id,
            )
        return records

    def change_state_done(self):
        """Set the subtask state to done."""
        for record in self:
            record.state = "done"

    def change_state_todo(self):
        """Set the subtask state to todo."""
        for record in self:
            record.state = "todo"

    def change_state_cancelled(self):
        """Set the subtask state to cancelled."""
        for record in self:
            record.state = "cancelled"

    def change_state_waiting(self):
        """Set the subtask state to waiting."""
        for record in self:
            record.state = "waiting"

    def action_delete(self):
        """Delete the current subtask records."""
        self.unlink()

    def action_convert_to_task(self):
        """Convert this checklist item into a child task of the parent task,
        then delete the checklist item."""
        state_map = {
            "done": "1_done",
            "cancelled": "1_canceled",
            "todo": "02_changes_requested",
            "waiting": "04_waiting_normal",
        }
        for record in self:
            record.task_id.write(
                {
                    "child_ids": [
                        Command.create(
                            {
                                "name": record.name,
                                "project_id": record.task_id.project_id.id,
                                "user_ids": [record.user_id.id],
                                "description": record.note or "",
                                "state": state_map.get(record.state, "01_in_progress"),
                            }
                        )
                    ]
                }
            )
            record.unlink()
