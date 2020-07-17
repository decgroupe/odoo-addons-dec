# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

import logging

from odoo import api, models
from odoo.exceptions import UserError

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
            note = error.name
            _logger.info(note)
            # Try to intercept exception
            redirections = self.env['procurement.exception'].search([])
            for redirection in redirections:
                if redirection.user_id and redirection.match(product_id, note):
                    self._log_next_activity(
                        product_id, note, redirection.user_id
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
