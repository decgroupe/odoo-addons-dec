# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import models, registry, _

import logging
_logger = logging.getLogger(__name__)

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _log_next_activity(self, product_id, note):
        """
        Override `_log_next_activity` from base in order to call it using a
        new cursor. It is necessary to do this since `_log_exception` himself
        is wrapped around a new cursor. During a transaction, we are not able
        to read committed data outside and during this transaction
        """
        # Create a new cursor to save this exception activity in database
        # even if we are in a transaction that will probably be rolled back
        cr = registry(self._cr.dbname).cursor()
        # Assign this cursor to self and all arguments to ensure consistent
        # data in all method
        self_cr = self.with_env(self.env(cr=cr))
        product_id = product_id.with_env(product_id.env(cr=cr))
        # Call super method
        super(StockRule, self_cr)._log_next_activity(product_id, note)
        # Commit this created activity to keep it even after a rollback
        cr.commit()
        cr.close()
