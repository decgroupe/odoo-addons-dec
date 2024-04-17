# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import api, models
from odoo.tools import safe_eval, is_html_empty

_logger = logging.getLogger(__name__)


class View(models.Model):
    _inherit = "ir.ui.view"

    def _render(self, values=None, engine="ir.qweb", minimal_qcontext=False):
        if minimal_qcontext:
            # even with a minimal context, we need some basic shortcuts !!!
            qcontext = self._prepare_minimal_qcontext()
            qcontext.update(values or {})
        else:
            qcontext = values
        res = super()._render(qcontext, engine, minimal_qcontext)
        return res

    @api.model
    def _prepare_minimal_qcontext(self):
        """Returns a minimal qcontext"""
        qcontext = dict(
            env=self.env,
            datetime=safe_eval.datetime,
            is_html_empty=is_html_empty,
        )
        return qcontext
