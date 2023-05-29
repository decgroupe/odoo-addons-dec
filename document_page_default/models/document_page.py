# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021


from odoo import _, api, fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model
    def _format_name(self, value):
        return "Rev {:02d}".format(value)

    @api.model
    def _default_draft_name(self):
        return self._format_name(1)

    @api.model
    def _default_draft_summary(self):
        return _("Init")

    draft_name = fields.Char(default=_default_draft_name)
    draft_summary = fields.Char(default=_default_draft_summary)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        return record

    def write(self, vals):
        result = super(DocumentPage, self).write(vals)
        return result

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        return super(DocumentPage, self).copy(default)

    def _create_history(self, vals):
        vals["name"] = self._format_name(len(self.history_ids) + 1)
        return super(DocumentPage, self)._create_history(vals)
