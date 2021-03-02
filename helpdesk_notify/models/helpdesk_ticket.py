# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import _, api, models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if self.env.context.get('fetchmail_cron_running'):
            if vals.get('team_id') and not vals.get('user_id'):
                team_id = self.env['helpdesk.ticket.team'].browse(
                    vals.get('team_id')
                )
                emails = []
                for user_id in team_id.user_ids:
                    emails.append(user_id.partner_id.email)
                    #res.message_subscribe(partner_ids=user_id.partner_id.ids)
                res.with_context(emails=','.join(emails)). \
                    send_user_internal_mail()
        return res

    def send_user_internal_mail(self):
        self.env.ref('helpdesk_notify.created_ticket_internal_template'). \
            send_mail(self.id, force_send=True)
