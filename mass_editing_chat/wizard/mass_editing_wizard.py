# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import _, api, models, fields
from odoo.tools import html2plaintext


class MassEditingWizard(models.TransientModel):
    _inherit = "mass.editing.wizard"

    chat_message = fields.Html(
        string="Note",
        help="Message that will be posted on the chat of each record",
    )
    chat_enabled = fields.Boolean()

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        mass_operation = self._get_mass_operation()
        TargetModel = self.env[mass_operation.model_id.model]
        res['chat_enabled'] = 'mail.thread' in TargetModel._inherit_module
        return res

    def _apply_operation(self, items):
        return super()._apply_operation(items)

    @api.model
    def create(self, vals):
        mass_editing = self._get_mass_operation()
        active_ids = self.env.context.get("active_ids", [])
        wizard = super().create(vals)
        # WARNING: The `create` method called from override `vals` with an
        # empty dict so nothing is saved during a create. That's why we must
        # use our vals to check for wizard data
        chat_message = vals.get('chat_message', False)
        # Convert to plain text to check text only content.
        # A security of 6 characters minimum is also added.
        post_chat_message = len(html2plaintext(chat_message).strip()) >= 6
        if active_ids:
            TargetModel = self.env[mass_editing.model_id.model]
            if post_chat_message:
                for target in TargetModel.browse(active_ids):
                    target.message_post(
                        body=chat_message, subtype="mail.mt_note"
                    )
        return wizard
