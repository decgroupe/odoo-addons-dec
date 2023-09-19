# Copyright 2021 DEC SARL, Inc - All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailActivityRedirection(models.Model):
    _name = "mail.activity.redirection"
    _description = "Mail Activity Redirection"
    _order = "sequence, id"

    active = fields.Boolean(
        string="Active",
        default=True,
        help="By unchecking the active field, you may hide a rule you will not use.",
    )
    name = fields.Char(translate=True)
    sequence = fields.Integer(
        string="Sequence",
        default=lambda self: self._default_sequence(),
        help="Gives the sequence order when displaying.",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        help="Activities will be redirected to this user",
        ondelete="cascade",
        required=True,
    )
    initial_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users initially targeted",
        context={"active_test": False},
    )
    model_ids = fields.Many2many(
        comodel_name="ir.model",
        string="Models",
        help="Models targeted by these activities like _name class attribute",
    )
    activity_type_ids = fields.Many2many(
        comodel_name="mail.activity.type",
        string="Activity Types",
    )
    qweb_templates = fields.Many2many(
        comodel_name="ir.ui.view",
        string="QWeb Templates",
        domain=[("type", "=", "qweb")],
        help="Templates used to render activity note",
    )
    regex_pattern = fields.Char(
        string="RegEx",
        default=lambda self: self._default_regex(),
        help="Regular Expression used to parse activity note",
    )
    activity_ids = fields.Many2many(
        comodel_name="mail.activity",
        copy=False,
        string="Intercepted Activities",
        help="History of latest intercepted and redirected activities",
    )

    @api.model
    def _default_sequence(self):
        rule = self.search([], limit=1, order="sequence DESC")
        return rule.sequence + 1

    @api.model
    def _default_regex(self):
        return ".*"

    def get_activity_type_xmlids(self):
        res = []
        for rec in self.filtered("activity_type_ids"):
            xml_ids = [
                value
                for key, value in rec.activity_type_ids.get_external_id().items()
                if value
            ]
            res += xml_ids
        return res

    def get_model_names(self):
        res = []
        for rec in self.filtered("model_ids"):
            for model_id in rec.model_ids:
                res.append(model_id.model)
        return res

    def get_qweb_template_xmlids(self):
        res = []
        for rec in self.filtered("qweb_templates"):
            for qweb_template in rec.qweb_templates:
                res.append(qweb_template.xml_id)
        return res

    def match(
        self,
        model_name,
        type_xmlid,
        type_id,
        user_id,
        qweb_template_xmlid,
        note,
    ):
        _logger.debug(
            "Match test against %s, %s, %s, %s, %s, %s",
            model_name,
            type_xmlid,
            type_id,
            user_id,
            qweb_template_xmlid,
            note,
        )
        self.ensure_one()
        if isinstance(note, bytes):
            note = note.decode("utf-8")
        res = True
        # Check if user match, even if `user_id` is None
        if res and self.initial_user_ids.ids:
            res = user_id in self.initial_user_ids.ids
        # Check if model match, even if `model_name` is None
        if res and model_name and self.model_ids.ids:
            res = model_name in self.get_model_names()
        # Check if activity types match
        if res and self.activity_type_ids.ids:
            if type_xmlid:
                res = type_xmlid in self.get_activity_type_xmlids()
            elif type_id:
                res = type_id in self.activity_type_ids.ids
            else:
                res = False
        # Check if qweb template match, even if `qweb_template_xmlid` is None
        if res and self.qweb_templates.ids:
            res = qweb_template_xmlid in self.get_qweb_template_xmlids()
        # Check if note match pattern
        if res and self.regex_pattern:
            if note:
                matches = re.search(self.regex_pattern, note, re.MULTILINE | re.DOTALL)
                if matches and matches.group(0):
                    res = True
                else:
                    res = False
            else:
                res = False
        return res
