# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import _, api, fields, models
from odoo.tools import html2plaintext


class MassEditingWizard(models.TransientModel):
    _inherit = "mass.editing.wizard"

    chat_message = fields.Html(
        string="Note",
        help="Message that will be posted on the chat of each record",
    )
    chat_enabled = fields.Boolean()

    @api.model
    def _get_thread_module_names(self):
        res = ["mail.thread", "mail.thread.cc", "mail.thread.blacklist"]
        return res

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        TargetModel = self.env[server_action.model_id.model]
        thread_modules = set(TargetModel._inherit_module) & set(
            self._get_thread_module_names()
        )
        res["chat_enabled"] = thread_modules and True or False
        return res

    def _apply_operation(self, items):
        return super()._apply_operation(items)

    @api.model
    def create(self, vals):
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        TargetModel = self.env[server_action.model_id.model]

        active_ids = self.env.context.get("active_ids", [])
        wizard = super().create(vals)
        # WARNING: The `create` method called from override `vals` with an
        # empty dict so nothing is saved during a create. That's why we must
        # use our vals to check for wizard data
        chat_message = vals.get("chat_message", False)
        # Convert to plain text to check text only content.
        # A security of 6 characters minimum is also added.
        post_chat_message = len(html2plaintext(chat_message).strip()) >= 6
        if active_ids:
            if post_chat_message:
                for target in TargetModel.browse(active_ids):
                    target.message_post(body=chat_message, subtype_xmlid="mail.mt_note")
        return wizard
