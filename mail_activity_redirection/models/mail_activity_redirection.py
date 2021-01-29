# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

import re
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailActivityRedirection(models.Model):
    _name = 'mail.activity.redirection'
    _description = "Mail Activity Redirection"
    _order = "sequence, id"

    active = fields.Boolean(
        'Active',
        default=True,
        help="By unchecking the active field, you may hide a "
        "rule you will not use."
    )
    name = fields.Char()
    sequence = fields.Integer(
        'Sequence',
        default=lambda self: self._default_sequence(),
        help="Gives the sequence order when displaying."
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        help="Activities will be redirected to this user",
        ondelete='cascade',
        required=True,
    )
    initial_user_ids = fields.Many2many(
        'res.users',
        string='Users initially targeted',
        domain=['|', ('active', '=', True), ('active', '=', False)],
    )
    model_id = fields.Many2one(
        'ir.model',
        help="Model name targeted by these activities "
        "like _name class attribute",
    )
    activity_type_id = fields.Many2one(
        'mail.activity.type',
        'Activity Type',
    )
    activity_type_xmlid = fields.Char(compute='_compute_activity_type_xmlid')
    qweb_template = fields.Many2one(
        'ir.ui.view',
        string="QWeb Template",
        domain=[('type', '=', 'qweb')],
        help="Template used to render activity note",
    )
    regex_pattern = fields.Char(
        string='RegEx',
        default=lambda self: self._default_regex(),
        help="Regular Expression used to parse activity note",
    )
    activity_ids = fields.Many2many(
        'mail.activity',
        string='Intercepted Activities',
        help="History of latest intercepted and redirected activities",
    )

    @api.model
    def _default_sequence(self):
        rule = self.search([], limit=1, order="sequence DESC")
        return rule.sequence + 1

    @api.model
    def _default_regex(self):
        return '.*'

    @api.multi
    def _compute_activity_type_xmlid(self):
        for rec in self.filtered('activity_type_id'):
            rec.activity_type_xmlid = \
                self.env['ir.model.data'].get_xmlid_as_string(
                    rec.activity_type_id)

    def match(self, model_name, type_xmlid, user_id, qweb_template_xmlid, note):
        _logger.info(
            'Match test against %s, %s, %s, %s, %s',
            model_name,
            type_xmlid,
            user_id,
            qweb_template_xmlid,
            note,
        )
        self.ensure_one()
        res = True
        if res and self.activity_type_xmlid:
            res = (type_xmlid == self.activity_type_xmlid)
        else:
            res = True
        if res and self.model_id:
            res = (model_name == self.model_id._name)
        else:
            res = True
        if res and self.initial_user_ids:
            res = (user_id in self.initial_user_ids.ids)
        else:
            res = True
        if res and self.qweb_template:
            if not qweb_template_xmlid and self.regex_pattern:
                # If no `qweb_template_xmlid` is found then continue if a
                # RegEx pattern is defined
                res = True
            else:
                res = (qweb_template_xmlid == self.qweb_template.xml_id)
        else:
            res = True
        if res and self.regex_pattern:
            matches = re.search(
                self.regex_pattern, note, re.MULTILINE | re.DOTALL
            )
            if matches and matches.group(0):
                res = True
            else:
                res = False
        return res
