# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

import re
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class BusinessException(models.Model):
    _name = 'business.exception'
    _description = "Business Exception"
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
        help="Exceptions will be redirected to this user",
        ondelete='cascade',
        required=True,
    )
    initial_user_ids = fields.Many2many(
        'res.users',
        string='Users initially targeted',
        domain=['|', ('active', '=', True), ('active', '=', False)],
    )
    model_name = fields.Char(
        help="Model name targeted by these exceptions "
        "like _name class attribute",
    )
    activity_template_xmlid = fields.Char(
        string='Activity XML ID',
        help="Exact XML ID name coded like module_name.template_name",
    )
    regex_pattern = fields.Char(
        string='RegEx',
        default=lambda self: self._default_regex(),
        help="Regular Expression used to parse business exception message",
    )
    activity_ids = fields.Many2many(
        'mail.activity',
        string='Intercepted Activities',
        help="History of latest intercepted activities",
    )

    @api.model
    def _default_sequence(self):
        rule = self.search([], limit=1, order="sequence DESC")
        return rule.sequence + 1

    @api.model
    def _default_regex(self):
        return '.*'

    def match(self, model_name, user_id, xmlid, message):
        _logger.info(
            'Match test against %s, %s, %s, %s',
            model_name,
            user_id,
            xmlid,
            message,
        )
        self.ensure_one()
        res = True
        if res and model_name and self.model_name:
            res = (model_name == self.model_name)
        else:
            res = True
        if res and user_id and self.initial_user_ids:
            res = (user_id in self.initial_user_ids.ids)
        else:
            res = True
        if res and xmlid and self.xmlid:
            res = (xmlid == self.xmlid)
        else:
            res = True
        if res and self.regex_pattern:
            matches = re.search(
                self.regex_pattern, message, re.MULTILINE | re.DOTALL
            )
            if matches and matches.group(0):
                res = True
        return res
