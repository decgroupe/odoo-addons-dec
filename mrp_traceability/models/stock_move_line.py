# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _log_message(self, record, move, template, vals):
        # built-in log_message method will call `message_post_with_view` on record
        # (not on self), so only its context is altered
        if (
            record.env.context.get("form_view_ref")
            == "mrp_traceability.stock_move_details_form_view"
        ):
            context = dict(record.env.context)
            # remove state from context to avoid unwanted side effects (since
            # `mail.tracking.email` also have a `state` field)
            context.pop("default_state", None)
            # pylint: disable=W8121
            record = record.with_context(context)
        res = super()._log_message(record, move, template, vals)
        return res
