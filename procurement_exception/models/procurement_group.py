# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

import logging

from odoo import api, models, registry, tools, _
from odoo.exceptions import UserError, MissingError
from psycopg2 import extensions

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
        except UserError as user_error:
            # Try to intercept and then re-raise exception
            self._try_intercept_exception(user_error, product_id)
        return res

    @api.model
    def _action_confirm_one_move(self, move):
        """ This method override existing one to catch UserError and call
        a custom implementation of _log_next_activity to redirect the error
        according to settings of this module.
        Redirection is built upon a regex string that is mapped to a user_id
        """
        try:
            product_id = move.product_id
        except MissingError:
            # When this function is called from a loop, then since
            # _action_confirm is allowed to merge moves with same
            # characteristics, the next moves can be already deleted
            # from database, so we ignore them
            return None
        try:
            with self._cr.savepoint():
                super()._action_confirm_one_move(move)
        except UserError as user_error:
            # Try to intercept and then re-raise exception
            self._try_intercept_exception(user_error, product_id)

    @api.model
    def _action_cannot_reorder_product(self, product_id):
        """ This method override existing one to catch UserError and call
        a custom implementation of _log_next_activity to redirect the error
        according to settings of this module.
        Redirection is built upon a regex string that is mapped to a user_id
        """
        try:
            with self._cr.savepoint():
                super()._action_cannot_reorder_product(product_id)
        except UserError as user_error:
            # Try to intercept and then re-raise exception
            self._try_intercept_exception(user_error, product_id)

    def _try_intercept_exception(self, user_error, product_id):
        message = user_error.name
        redirections = self.env['procurement.exception'].search([])
        for redirection in redirections:
            if redirection.user_id and redirection.match(product_id, message):
                self._log_exception(product_id, message, redirection.user_id)
                # Stop after first match
                break
        # We can finally re-raise UserError even if we are possibly in a
        # transaction because exception has been logged using a new
        # database cursor.
        # (note that _log_next_activity implementation from stock.rule
        # also check for an existing activty).
        raise user_error

    def _log_exception(self, product_id, message, user_id):
        # Create a new cursor to save this exception activity in database
        # even if we are in a transaction that will probably be rolled back
        cr = registry(self._cr.dbname).cursor()
        # Assign this cursor to self and all arguments to ensure consistent
        # data in all method
        self = self.with_env(self.env(cr=cr))
        product_id = product_id.with_env(product_id.env(cr=cr))
        user_id = user_id.with_env(user_id.env(cr=cr))

        #note = tools.plaintext2html(message)
        note = message
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
            # Will be None if this warning activity type has been deleted
            activity_type_id = self.env.ref(
                'mail.mail_activity_data_warning', raise_if_not_found=False
            )
            _logger.info(
                "Creating new exception (Activity): {}: {}".format(
                    product_id.product_tmpl_id.display_name,
                    note,
                )
            )
            activity_data = {
                'activity_type_id': activity_type_id and \
                    activity_type_id.id or False,
                'note': note,
                'summary': _('Exception'),
                'user_id': user_id.id,
                'res_id': product_id.product_tmpl_id.id,
                'res_model_id': model_product_template.id,
            }
            _logger.debug(activity_data)
            MailActivity.create(activity_data)
        # Commit this created activity to keep it even after a rollback
        cr.commit()
        cr.close()
