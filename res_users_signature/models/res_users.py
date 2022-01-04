# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

import base64
import os
import logging
from pathlib import Path

from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


def removeprefix(self: str, prefix: str) -> str:
    if self.startswith(prefix):
        return self[len(prefix):]
    else:
        return self[:]


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
    signature_logo = fields.Binary(
        string='Signature Logo',
        help="Logo used to replace the one used to render the user signature",
        attachment=False,
    )
    signature_logo_filename = fields.Char(
        string='Signature Logo Filename',
        help="Technical field only used to get the original file name "
        "and extension",
    )

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(
                self.SELF_WRITEABLE_FIELDS + [
                    'signature_text', 'signature_answer', 'signature_logo',
                    'signature_logo_filename'
                ]
            )
        )
        return init_res

    def _generate_from_template(self, template):
        self.ensure_one()
        self.signature = template._render_template(template.body_html, self.id)
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

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'signature_logo' in vals:
            fname = self.write_signature_logo_to_fs(
                vals.get('signature_logo'),
                vals.get('signature_logo_filename'),
            )
            # Update the filename with the one given on the filesystem
            self.signature_logo_filename = fname
        return res

    def _get_signature_logo_path(self, logo_filename=None):
        path = Path(os.path.dirname(__file__))
        root_path = str(path.parent.parent)
        path = os.path.join(path.parent, 'static', 'img', 'sig')
        if not os.path.exists(path):
            os.makedirs(path)

        fname = '%d' % (self.id)
        if logo_filename:
            logo_name, logo_ext = os.path.splitext(logo_filename)
            fname += logo_ext.lower()
        full_path = os.path.join(path, fname)
        module_fname = removeprefix(full_path, root_path)
        return module_fname, full_path

    def write_signature_logo_to_fs(self, value, filename):
        module_fname, full_path = self._get_signature_logo_path(filename)
        if not value and os.path.exists(full_path):
            os.remove(full_path)
        elif value:
            if isinstance(value, tools.pycompat.text_type):
                value = value.encode('ascii')
            value = tools.image_resize_image(value, size=(87, 87))
            bin_value = base64.b64decode(value)
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return module_fname
