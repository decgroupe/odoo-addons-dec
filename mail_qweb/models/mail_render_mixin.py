# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

from odoo import api, fields, models, tools

from odoo.addons.mail.models.mail_render_mixin import format_date

_logger = logging.getLogger(__name__)


def remaining_days(record, date, date_format=False, lang_code=False):
    now = fields.Date.context_today(record)
    diff = date - now
    if abs(diff.days) > 99:
        value = format_date(record.env, date, date_format, lang_code)
    elif diff.days == 0:
        value = record.env._("Today")
    elif diff.days < 0:
        if diff.days == -1:
            value = record.env._("Yesterday")
        else:
            value = record.env._("%d days ago") % (-diff.days)
    else:
        if diff.days == 1:
            value = record.env._("Tomorrow")
        else:
            value = record.env._("In %d days") % (diff.days)
    return value


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    @api.model
    def _render_eval_context(self):
        render_context = super()._render_eval_context()
        render_context.update(
            {
                "is_html_empty": tools.is_html_empty,
                "remaining_days": lambda date,
                date_format=False,
                lang_code=False: remaining_days(  # noqa: E501
                    self, date, date_format, lang_code
                ),
            }
        )
        return render_context

    @api.model
    def _render_record_context(self, record, common_variables):
        record_context = super()._render_record_context(record, common_variables)
        pre_render_results = self.env.context.get("pre_render_results")
        if pre_render_results and record.id in pre_render_results:
            record_context.update(pre_render_results[record.id])
        if hasattr(record, "_notify_get_action_link"):
            record_context["access_link"] = record._notify_get_action_link("view")
        else:
            record_context["access_link"] = False
        return record_context

    def _render_field(
        self,
        field,
        res_ids,
        engine="inline_template",
        compute_lang=False,
        set_lang=False,
        add_context=None,
        options=None,
    ):
        if add_context is None:
            add_context = {}
        add_context["sender"] = self
        res = super()._render_field(
            field=field,
            res_ids=res_ids,
            engine=engine,
            compute_lang=compute_lang,
            set_lang=set_lang,
            add_context=add_context,
            options=options,
        )
        return res
