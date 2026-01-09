# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = "mail.template"

    no_inline_css = fields.Boolean(
        string="No inline CSS",
        help="If checked, all styles will be kept as-is and no premailer will "
        "be processed",
    )

    def _premailer_apply_transform(self, html):
        no_inline_css = self.env.context.get("no_inline_css", self.no_inline_css)
        if no_inline_css:
            return html
        else:
            return super()._premailer_apply_transform(html)

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        email_layout_xmlid=False,
    ):
        """When `email_layout_xmlid` is `False`, no `_render_template_postprocess` is
        called. That's why we need to override `generate_email`
        TODO: Check if this assumption is still valid (test ?) in Odoo 18 since
        `_render_template_postprocess` is now called if `options.get('post_process')`
        is not False.
        """
        self.ensure_one()
        return super(
            MailTemplate,
            self.with_context(
                # keep trace of the template
                mail_template_id=self.id,
                force_replace_local_links=not email_layout_xmlid,
            ),
        ).send_mail(
            res_id, force_send, raise_exception, email_values, email_layout_xmlid
        )

    def _get_pre_rendered_fields(self):
        """Fields to pre-render before generating the template"""
        return ["subject"]

    # Was named generate_email in Odoo 14.0
    def _generate_template(self, res_ids, render_fields, find_or_create_partners=False):
        """Override to pre-render some fields (like `subject`)"""
        pre_render_results = self.env.context.get("pre_render_results", {})
        pre_render_fields = self._get_pre_rendered_fields()
        for _lang, (template, template_res_ids) in self._classify_per_lang(
            res_ids
        ).items():
            fields_torender = {field for field in pre_render_fields}
            for field in fields_torender:
                generated_field_values = template._render_field(field, template_res_ids)
                for res_id, field_value in generated_field_values.items():
                    pre_render_results.setdefault(res_id, {})[field] = field_value
        result = super(
            MailTemplate, self.with_context(pre_render_results=pre_render_results)
        )._generate_template(
            res_ids,
            render_fields,
            find_or_create_partners=find_or_create_partners,
        )
        if self.env.context.get("force_replace_local_links"):
            for res_id in res_ids:
                if result[res_id].get("body_html"):
                    result[res_id]["body_html"] = self.env[
                        "mail.render.mixin"
                    ]._replace_local_links(result[res_id]["body_html"])
        return result

    def _render_template(
        self,
        template_src,
        model,
        res_ids,
        engine="inline_template",
        add_context=None,
        options=None,
    ):
        return super()._render_template(
            template_src,
            model,
            res_ids,
            engine=engine,
            add_context=add_context,
            options=options,
        )
