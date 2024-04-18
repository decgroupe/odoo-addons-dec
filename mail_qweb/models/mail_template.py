# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import models, tools

_logger = logging.getLogger(__name__)

class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _render_qweb_body_eval_context(self, record):
        render_context = super()._render_qweb_body_eval_context(record)
        render_context.update(
            {
                # we also need the mail subject in our custom templates
                "subject": self._render_field("subject", record.ids)[record.id],
                "is_html_empty": tools.is_html_empty,
                "access_link": hasattr(record, "_notify_get_action_link")
                and record._notify_get_action_link("view")
                or False,
            }
        )
        return render_context

    def _render_qweb_body(
        self, res_ids, compute_lang=False, set_lang=False, post_process=False
    ):
        # will also apply premailer before Odoo opens its html editor
        res = super()._render_qweb_body(
            res_ids=res_ids,
            compute_lang=compute_lang,
            set_lang=set_lang,
            post_process=post_process,
        )
        for res_id, rendered in res.items():
            res[res_id] = self._premailer_apply_transform(tools.ustr(rendered))
        return res

    def _render_field(
        self, field, res_ids, compute_lang=False, set_lang=False, post_process=False
    ):
        res = super()._render_field(
            field=field,
            res_ids=res_ids,
            compute_lang=compute_lang,
            set_lang=set_lang,
            post_process=post_process,
        )
        for res_id in res_ids:
            _logger.debug("=> Renderered field %s: %s", field, res[res_id])
        return res
