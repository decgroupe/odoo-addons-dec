# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging


from odoo import models, tools, _
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)


class MailMail(models.AbstractModel):
    _inherit = "mail.mail"

    def _send_prepare_body(self):
        if self.model == "mail.channel" and self.res_id:
            # no super() call on purpose, no private links that could be quoted!
            channel = self.env["mail.channel"].browse(self.res_id)
            return self._send_prepare_body_channel(channel)
        else:
            return super(MailMail, self)._send_prepare_body()

    def _send_prepare_body_channel(self, channel):
        """Override body rendering for channel emails."""
        vals = self._get_channel_footer_vals(channel)
        footer = self._get_channel_footer_string(vals)
        # unlike odoo, we use the `body_html` content (the one with the layout)
        body = tools.append_content_to_html(
            self.body_html, footer, plaintext=False, container_tag="div"
        )
        # also replace local links (odoo miss that too)
        body = self.env["mail.render.mixin"]._replace_local_links(body)
        return body

    def _get_channel_footer_vals(self, channel):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return {
            "maillist": _("Mailing-List"),
            "post_to": _("Post to"),
            "unsub": _("Unsubscribe"),
            "mailto_url": "mailto:%s@%s" % (channel.alias_name, channel.alias_domain),
            "group_url": "%s/groups/%s" % (base_url, slug(channel)),
            "unsub_url": "%s/groups?unsubscribe" % (base_url,),
            "channel": channel.name,
            "channel_mail": "%s@%s" % (channel.alias_name, channel.alias_domain),
        }

    def _get_channel_footer_string(self, vals):
        return (
            """______________________________<br/>
                <small>
                <a href=%(group_url)s>#%(channel)s</a> |
                <a href=%(mailto_url)s>%(channel_mail)s</a>
                </small>
            """
            % vals
        )
