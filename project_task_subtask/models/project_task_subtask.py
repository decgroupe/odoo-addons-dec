# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 manawi <https://github.com/manawi>
# Copyright 2017-2018 Karamov Ilmir <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018 iledarn <https://github.com/iledarn>
# Copyright 2017 Nicolas JEUDY <https://github.com/njeudy>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _

SUBTASK_STATES = {
    "done": _("Done"),
    "todo": _("To-Do"),
    "waiting": _("Waiting"),
    "cancelled": _("Cancelled"),
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
        index="1",
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

    def _compute_recolor(self):
        self.recolor = False
        for record in self:
            if self.env.user == record.user_id and record.state == "todo":
                record.recolor = True

    def _compute_hide_button(self):
        self.hide_button = False
        for record in self:
            if (
                self.env.user not in [record.reviewer_id, record.user_id]
                and not self.env.user._is_admin()
            ):
                record.hide_button = True

    def _compute_reviewer_id(self):
        self.reviewer_id = False
        for record in self:
            record.reviewer_id = record.create_uid

    @api.model
    def _needaction_domain_get(self):
        if self._needaction:
            return [("state", "=", "todo"), ("user_id", "=", self.env.uid)]
        return []

    def write(self, vals):
        old_names = dict(list(zip(self.mapped("id"), self.mapped("name"))))
        result = super(ProjectTaskSubtask, self).write(vals)
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
                        _("Only users related to that subtask can change " "the state.")
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
                        _("Only users related to that subtask can change " "the name.")
                    )
            if vals.get("user_id"):
                r.task_id.send_subtask_email(
                    r.name, r.state, r.reviewer_id.id, r.user_id.id
                )
        return result

    @api.model
    def create(self, vals):
        result = super(ProjectTaskSubtask, self).create(vals)
        vals = self._add_missing_default_values(vals)
        task = self.env["project.task"].browse(vals.get("task_id"))
        task.send_subtask_email(
            vals["name"], vals["state"], vals["reviewer_id"], vals["user_id"]
        )
        return result

    def change_state_done(self):
        for record in self:
            record.state = "done"

    def change_state_todo(self):
        for record in self:
            record.state = "todo"

    def change_state_cancelled(self):
        for record in self:
            record.state = "cancelled"

    def change_state_waiting(self):
        for record in self:
            record.state = "waiting"

    def action_delete(self):
        self.unlink()
