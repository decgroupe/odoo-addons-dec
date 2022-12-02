# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import re
import string

from odoo import models, fields, api, _


class DocumentPage(models.Model):
    _inherit = 'document.page'

    @api.model
    def _default_draft_name(self):
        return "Rev 01"

    @api.model
    def _default_draft_summary(self):
        return _("Init")

    draft_name = fields.Char(default=_default_draft_name)
    draft_summary = fields.Char(default=_default_draft_summary)

    def write(self, vals):
        if not 'draft_name' in vals:
            vals['draft_name'] = "Rev {:02d}".format(len(self.history_ids) + 1)
        result = super(DocumentPage, self).write(vals)
        return result