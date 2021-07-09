# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    signature_text = fields.Text(
        string='Text Signature',
        help="This field is only used on reports when the report engine does "
        "not support html rendering",
    )
    signature_answer = fields.Html(
        string='Answer Signature',
        help="Lightweight version of the HTML signature",
    )
    signature_template = fields.Many2one(
        string='Signature Template',
        comodel_name='res.users.signature.template',
    )
    signature_social_buttons = fields.Boolean(
        string='Social Buttons on Signature',
        help="Add company social links to the HTML signature",
    )

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(
                self.SELF_WRITEABLE_FIELDS +
                ['signature_text', 'signature_answer']
            )
        )
        return init_res

    def _generate_from_template(self, template):
        self.ensure_one()
        self.signature = template._render_template(
            template.body_html, self.id
        )
        self.signature_answer = template._render_template(
            template.body_lightweight_html, self.id
        )
        self.signature_text = template.with_context(
            safe=True
        )._render_template(template.body_text, self.id)

    @api.multi
    def action_generate_signatures(self):
        global_template = self.env.ref(
            'res_users_signature.user_signature_template'
        )
        for user in self:
            template = user.signature_template or global_template
            user._generate_from_template(template)
