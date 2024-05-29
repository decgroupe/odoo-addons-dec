# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024


from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # yapf: disable
    def _notify_compute_recipients(self, message, msg_vals):
        """Hook Odoo computation in order to re-add partner with
        `notification_type=inbox`when the channel has `email_send` enabled.
        Please note that duplicates should not exists as the `exept_partner` is here
        to avoid that.
        /!\ Only the SQL query has been edited
        """
        recipient_data = super()._notify_compute_recipients(message, msg_vals)
        author_id = msg_vals.get('author_id') or message.author_id.id
        email_cids = [r['id'] for r in recipient_data['channels'] if r['notif'] == 'email']
        if email_cids:
            email_from = msg_vals.get('email_from') or message.email_from
            email_from = self.env['res.partner']._parse_partner_name(email_from)[1]
            exept_partner = [r['id'] for r in recipient_data['partners']]
            if author_id:
                exept_partner.append(author_id)

            sql_query = """ select distinct on (p.id) p.id from res_partner p
                            left join mail_channel_partner mcp on p.id = mcp.partner_id
                            left join mail_channel c on c.id = mcp.channel_id
                            left join res_users u on p.id = u.partner_id
                                where (u.notification_type = 'inbox' or u.id is null)
                                and c.email_send
                                and (p.email != ANY(%s) or p.email is null)
                                and c.id = ANY(%s)
                                and not p.id = ANY(%s)"""

            self.env.cr.execute(sql_query, (([email_from], ), (email_cids, ), (exept_partner, )))
            for partner_id in self._cr.fetchall():
                # ocn_client: will add partners to recipient recipient_data. more ocn notifications. We neeed to filter them maybe
                recipient_data['partners'].append({'id': partner_id[0], 'share': True, 'active': True, 'notif': 'email', 'type': 'channel_email', 'groups': []})

        return recipient_data
    # yapf: enable
