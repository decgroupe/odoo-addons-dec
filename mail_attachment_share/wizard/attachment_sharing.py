# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo import api, fields, models


class AttachmentSharing(models.TransientModel):
    _name = "attachment.sharing"
    _description = "Attachment Sharing Wizard"

    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        readonly=True,
        string="Attachments",
    )

    @api.model
    def default_get(self, fields):
        res = super(AttachmentSharing, self).default_get(fields)
        context = self._context or {}
        res_model = context.get("default_res_model")
        res_id = context.get("default_res_id")
        if res_model and res_id:
            domain = [
                ("res_id", "=", res_id),
                ("res_model", "=", res_model),
            ]
            attachment_ids = self.env["ir.attachment"].search(domain)
            res["attachment_ids"] = [(6, 0, attachment_ids.ids)]

        return res

    def _reopen(self, id=False):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_id": id or self.id,
            "res_model": self._name,
            "target": "new",
            "context": {
                "default_model": self._name,
            },
        }