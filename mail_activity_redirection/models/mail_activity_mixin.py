# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    def activity_schedule(self, act_type_xmlid='', date_deadline=None, \
        summary='', note='', **act_values):
        """ Compare values used to create a new activity with the ones in
            mail activity redirection rules. If a match is set then
            assign a different user to this activity.
        """
        _logger.debug('activity_schedule')
        mail_activity_redirection = False
        redirections = self.env['mail.activity.redirection'].search([])
        for redirection in redirections:
            if redirection.user_id and redirection.match(
                self._name,
                act_type_xmlid,
                act_values.get('user_id'),
                act_values.get('stored_act_type_xmlid'),
                note.decode('utf-8'),
            ):
                # Replace User with the one set in redirection rule
                act_values['user_id'] = redirection.user_id.id
                # Keep a reference on this redirection to assign created
                # activities
                mail_activity_redirection = redirection
                # Stop after first match
                break
        activity_ids = super().activity_schedule(
            act_type_xmlid, date_deadline, summary, note, **act_values
        )
        activity_ids._link_to_mail_activity_redirection(mail_activity_redirection)
        return activity_ids

    def activity_schedule_with_view(self, act_type_xmlid='', \
        date_deadline=None, summary='', views_or_xmlid='', \
        render_context=None, **act_values):
        """ Basic hook to keep a value of the original xmlid before its use
            for rendering.
        """
        _logger.debug('activity_schedule_with_view')
        # Store act_type_xmlid for possible use in activity_schedule
        act_values['stored_act_type_xmlid'] = act_type_xmlid
        return super().activity_schedule_with_view(
            act_type_xmlid, date_deadline, summary, views_or_xmlid,
            render_context, **act_values
        )
