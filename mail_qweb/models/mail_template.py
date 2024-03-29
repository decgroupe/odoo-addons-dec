# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

from odoo import models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields):
        # also apply premailer before Odoo opens its html editor
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False
        result = super(MailTemplate, self).generate_email(res_ids, fields=fields)

        for res_id in res_ids:
            if self.body_type == "qweb" and (not fields or "body_html" in fields):
                result[res_id]["body_html"] = self._premailer_apply_transform(
                    result[res_id]["body_html"]
                )
        return result if multi_mode else result[res_ids[0]]
