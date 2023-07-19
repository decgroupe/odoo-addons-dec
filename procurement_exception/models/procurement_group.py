# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, models
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import MissingError, UserError


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        """This method override existing one to catch UserError and call
        `_log_redirected_exception` to redirect the error according to settings of this
        module. Redirection is built upon a regex string that is mapped to a user_id
        """
        res = False
        try:
            with self._cr.savepoint():
                # Override `raise_user_error` to always get a ProcurementException
                res = super().run(procurements, raise_user_error=False)
        except ProcurementException as proc_except:
            # Try to intercept and then re-raise the same exception but rebuilt from
            # scratch (ProcurementException -> UserError) if `raise_user_error=True`
            self._try_intercept_exception(proc_except, raise_user_error)
        return res

    @api.model
    def _action_confirm_one_move(self, move):
        """This method override existing one to catch UserError and call
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
            # Try to intercept and then re-raise exception if needed
            self._try_intercept_user_error(user_error, product_id)

    @api.model
    def _action_cannot_reorder_product(self, product_id):
        """This method override existing one to catch UserError and call
        a custom implementation of _log_next_activity to redirect the error
        according to settings of this module.
        Redirection is built upon a regex string that is mapped to a user_id
        """
        try:
            with self._cr.savepoint():
                super()._action_cannot_reorder_product(product_id)
        except UserError as user_error:
            # Try to intercept and then re-raise exception if needed
            self._try_intercept_user_error(user_error, product_id)

    def _try_intercept_user_error(self, user_error, product_id, raise_user_error=True):
        error = user_error.name
        redirections = self.env["procurement.exception"].search([])
        for redirection in redirections:
            if redirection.user_id and redirection.match(product_id, error):
                self._log_exception(product_id, error, redirection.user_id)
                raise_user_error = False
                # Stop after first match
                break
        if raise_user_error:
            # The exception is re-raised only if no redirection was found before
            raise user_error

    def _try_intercept_exception(self, proc_except, raise_user_error):
        procurement_errors = proc_except.procurement_exceptions
        for procurement, error in procurement_errors:
            product_id = procurement.product_id
            self._log_redirected_exception(procurement.product_id, error)
        # We can finally re-raise the original exception or convert it to `UserError`
        # if requested by `raise_user_error`
        if raise_user_error:
            dummy, errors = zip(*procurement_errors)
            raise UserError("\n".join(errors))
        else:
            raise proc_except

    def _log_redirected_exception(self, product_id, error):
        redirections = self.env["procurement.exception"].search([])
        for redirection in redirections:
            if redirection.user_id and redirection.match(product_id, error):
                self._log_exception(product_id, error, redirection.user_id)
                # Stop after first redirection match
                break
