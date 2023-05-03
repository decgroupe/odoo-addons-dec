# Copyright 2017-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2017-2018 manawi <https://github.com/manawi>
# Copyright 2017-2018 Karamov Ilmir <https://it-projects.info/team/ilmir-k>
# Copyright 2017-2018 iledarn <https://github.com/iledarn>
# Copyright 2017 Nicolas JEUDY <https://github.com/njeudy>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools import html_escape as escape
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
        default=lambda self: self.env.user
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
    hide_button = fields.Boolean(compute="_compute_hide_button", )
    recolor = fields.Boolean(compute="_compute_recolor", )
    deadline = fields.Datetime(string="Deadline", )

    def _compute_recolor(self):
        self.recolor = False
        for record in self:
            if self.env.user == record.user_id and record.state == "todo":
                record.recolor = True

    def _compute_hide_button(self):
        self.hide_button = False
        for record in self:
            if (
                self.env.user not in [record.reviewer_id, record.user_id] and
                not self.env.user._is_admin()
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
                    self.env.user == r.reviewer_id or
                    self.env.user == r.user_id or self.env.user._is_admin()
                ):
                    raise UserError(
                        _(
                            "Only users related to that subtask can change "
                            "the state."
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
                    self.env.user == r.reviewer_id or
                    self.env.user == r.user_id or self.env.user._is_admin()
                ):
                    raise UserError(
                        _(
                            "Only users related to that subtask can change "
                            "the name."
                        )
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


class Task(models.Model):
    _inherit = "project.task"

    subtask_ids = fields.One2many(
        comodel_name="project.task.subtask",
        inverse_name="task_id",
        string="Subtask",
    )
    kanban_subtasks = fields.Text(compute="_compute_kanban_subtasks", )
    default_user = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_default_user",
    )
    completion = fields.Integer(
        string="Completion",
        compute="_compute_completion",
    )
    completion_xml = fields.Text(compute="_compute_completion_xml", )

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
                    self.env.user == record.create_uid and
                    self.env.user == record.user_id
                ):
                    record.default_user = self.env.user

    def _compute_kanban_subtasks(self):
        self.kanban_subtasks = ""
        for record in self:
            result_string_td = ""
            result_string_wt = ""
            if record.subtask_ids:
                task_todo_ids = record.subtask_ids.filtered(
                    lambda x: x.state == "todo" and x.user_id.id == record.env.
                    user.id
                )
                task_waiting_ids = record.subtask_ids.filtered(
                    lambda x: x.state == "waiting" and x.user_id.id == record.
                    env.user.id
                )
                if task_todo_ids:
                    tmp_string_td = escape(": {}".format(len(task_todo_ids)))
                    result_string_td += _("<li><b>To-Do{}</b></li>"
                                         ).format(tmp_string_td)
                if task_waiting_ids:
                    tmp_string_wt = escape(": {}".format(len(task_waiting_ids)))
                    result_string_wt += _("<li><b>Waiting{}</b></li>"
                                         ).format(tmp_string_wt)
            record.kanban_subtasks = (
                '<div class="kanban_subtasks"><ul>' + result_string_td +
                result_string_wt + "</ul></div>"
            )

    def _compute_completion(self):
        for record in self:
            record.completion = record.task_completion()

    def _compute_completion_xml(self):
        self.completion_xml = ""
        for record in self:
            active_subtasks = record.subtask_ids and record.subtask_ids.filtered(
                lambda x: x.user_id.id == record.env.user.id and x.state !=
                "cancelled"
            )
            if not active_subtasks:
                record.completion_xml = """
                    <div class="task_progress">
                    </div>
                    """
                continue

            completion = record.task_completion()
            color = "bg-success-full"
            if completion < 50:
                color = "bg-danger-full"
            header = _("Your Checklist:")
            record.completion_xml = """
            <div class="task_progress">
                <div class="progress_info">
                    {2}
                </div>
                <div class ="o_kanban_counter_progress progress task_progress_bar">
                    <div data-filter="done"
                         class ="progress-bar {1} o_bar_has_records task_progress_bar_done"
                         data-original-title="1 done"
                         style="width: {0}%;">
                    </div>
                    <div data-filter="blocked"
                         class ="progress-bar bg-danger-full"
                         data-original-title="0 blocked">
                    </div>
                </div>
                <div class="task_completion"> {0}% </div>
            </div>
            """.format(int(completion), color, header)

    def task_completion(self):
        user_task_ids = self.subtask_ids.filtered(
            lambda x: x.user_id.id == self.env.user.id and x.state !=
            "cancelled"
        )
        if not user_task_ids:
            return 100
        user_done_task_ids = user_task_ids.filtered(lambda x: x.state == "done")
        return (len(user_done_task_ids) / len(user_task_ids)) * 100

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
                body = "<p>" + "<strong>" + state + "</strong>: " + escape(
                    subtask_name
                )
                subtype_xmlid = False
            elif self.env.user == reviewer:
                body = (
                    "<p>" + escape(user.name) + ", <br><strong>" + state +
                    "</strong>: " + escape(subtask_name)
                )
                partner_ids = [user.partner_id.id]
            elif self.env.user == user:
                msg = _("I updated checklist item assigned to me")
                body = (
                    "<p>" + escape(reviewer.name) +
                    ', <em style="color:#999">' + msg + ":</em> <br><strong>" +
                    state + "</strong>: " + escape(subtask_name)
                )
                partner_ids = [reviewer.partner_id.id]
            else:
                msg = _("I updated checklist item, now its assigned to")
                body = (
                    "<p>" + escape(user.name) + ", " + escape(reviewer.name) +
                    ', <em style="color:#999">' + msg + " " +
                    escape(user.name) + ": </em> <br><strong>" + state +
                    "</strong>: " + escape(subtask_name)
                )
                partner_ids = [user.partner_id.id, reviewer.partner_id.id]
            if old_name:
                msg = _("Updated from")
                body = (
                    body + '<br><em style="color:#999">' + msg +
                    "</em><br><strong>" + state + "</strong>: " +
                    escape(old_name) + "</p>"
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
