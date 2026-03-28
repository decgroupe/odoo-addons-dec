# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class DocumentPage(models.Model):
    _inherit = "document.page"

    draft_name = fields.Char(
        string="Name",
        help="Name for the changes made",
        readonly=False,
        default=lambda self: self._default_draft_name(),
    )

    draft_summary = fields.Char(
        string="Summary",
        help="Describe the changes made",
        readonly=False,
        default=lambda self: self._default_draft_summary(),
    )

    @api.model
    def _default_draft_name(self):
        return self._format_name(1)

    @api.model
    def _default_draft_summary(self):
        return self.env._("Init")

    @api.model
    def _format_name(self, value):
        """Format a revision number as a human-readable string."""
        return f"Rev {value:02d}"

    def _create_history(self, vals):
        """Override to set the history name as a formatted revision number."""
        history = super()._create_history(vals)
        self.invalidate_recordset(["history_ids"])
        history.name = self._format_name(len(self.history_ids))
        return history
