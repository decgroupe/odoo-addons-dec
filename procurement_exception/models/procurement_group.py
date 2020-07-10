# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Jul 2020

from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, \
        name, origin, values):
        """ This method override existing one to catch UserError and call
        a custom implementation of _log_next_activity to redirect the error
        according to settings of this module.
        Redirection is built upon a regex string that is mapped to a user_id
        """
        res = False
        try:
            with self._cr.savepoint():
                res = super().run(product_id, product_qty, product_uom, \
                    location_id, name, origin, values)
        except UserError as error:
            message = error.name
            _logger.info(message)
            # Try to intercept exception
            redirections = self.env['procurement.exception'].search([])
            for redirection in redirections:
                if redirection.user_id and redirection.match(message):
                    self._log_next_activity(
                        product_id, message, redirection.user_id
                    )
                    # Stop after first match
                    break
            # We cannot call raise UserError since we are in a transaction
            # so we call _log_next_activity ourself.
            # (note that implementation from stock.rule also check for an
            # existing activty).
            self.env['stock.rule']._log_next_activity(product_id, error.name)
        return res

    def _log_next_activity(self, product_id, note, user_id):
        MailActivity = self.env['mail.activity']
        model_product_template = self.env.ref('product.model_product_template')
        existing_activity = MailActivity.search(
            [
                ('res_id', '=', product_id.product_tmpl_id.id),
                ('res_model_id', '=', model_product_template.id),
                ('note', '=', note),
                ('user_id', '=', user_id.id),
            ]
        )
        if not existing_activity:
            # If the user deleted todo activity type.
            try:
                activity_type_id = self.env.ref('mail.mail_activity_data_todo')
            except:
                activity_type_id = False

            MailActivity.create(
                {
                    'activity_type_id': activity_type_id.id,
                    'note': note,
                    'user_id': user_id.id,
                    'res_id': product_id.product_tmpl_id.id,
                    'res_model_id': model_product_template.id,
                }
            )
