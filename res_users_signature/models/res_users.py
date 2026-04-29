# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

import os

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    signature_text = fields.Text(
        string="Text Signature",
        help="This field is only used on reports when the report engine does "
        "not support html rendering",
    )
    signature_answer = fields.Html(
        string="Answer Signature",
        help="Lightweight version of the HTML signature",
    )
    signature_template = fields.Many2one(
        string="Signature Template",
        comodel_name="res.users.signature.template",
    )
    signature_social_buttons = fields.Boolean(
        string="Social Buttons on Signature",
        default=True,
        help="Add company social links to the HTML signature",
    )
    signature_logo = fields.Binary(
        string="Signature Logo",
        help="Logo used to replace the one used to render the user signature",
        attachment=False,
    )
    signature_logo_filename = fields.Char(
        string="Signature Logo Filename",
        help="Technical field only used to get the original file name " "and extension",
    )

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Extend writable fields to include all signature-related fields."""
        return super().SELF_WRITEABLE_FIELDS + [
            "signature_text",
            "signature_answer",
            "signature_template",
            "signature_social_buttons",
            "signature_logo",
            "signature_logo_filename",
        ]

    def _generate_from_template(self, template, origin_user_id=False):
        """Generate all signature fields from a template for this user."""
        self.ensure_one()
        if not template:
            return
        if not origin_user_id:
            origin_user_id = self
        self.signature = template._render_template(
            template.body_html, origin_user_id.id
        )
        self.signature_answer = template._render_template(
            template.body_lightweight_html, origin_user_id.id
        )
        self.signature_text = template.with_context(safe=True)._render_template(
            template.body_text, origin_user_id.id
        )

    def action_generate_signatures(self):
        """Action to regenerate all signature fields using the user's template
        or the global one."""
        global_template = self.env.ref("res_users_signature.user_signature_template")
        for user in self:
            template = user.signature_template or global_template
            user._generate_from_template(template)

    @api.onchange("signature_template")
    def onchange_signature_template(self):
        """Regenerate signatures when the signature template changes."""
        self._generate_from_template(self.signature_template, self._origin)

    def write(self, vals):
        """Override write to sync the logo filename when signature_logo changes."""
        res = super().write(vals)
        if "signature_logo" in vals:
            # Update the filename with the one given on the filesystem
            self.signature_logo_filename = self._get_signature_logo_filename(
                vals.get("signature_logo_filename")
            )
        return res

    def _get_signature_logo_filename(self, logo_filename=None):
        """Return the filename used to serve the signature logo over HTTP."""
        fname = "%d" % (self.id)
        if logo_filename:
            logo_name, logo_ext = os.path.splitext(logo_filename)
            fname += logo_ext.lower()
        return fname
