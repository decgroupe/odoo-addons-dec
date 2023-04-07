# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

import logging

from odoo import _, api, models, registry, tools
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.exceptions import MissingError, UserError

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        """This method override existing one to catch UserError and call
        a custom implementation of _log_next_activity to redirect the error
        according to settings of this module.
        Redirection is built upon a regex string that is mapped to a user_id
        """
        res = False
        try:
            with self._cr.savepoint():
                # Override `raise_user_error` to always get a ProcurementException
                res = super().run(procurements, raise_user_error=False)
        except ProcurementException as proc_except:
            # Try to intercept and then re-raise exception
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
            # Try to intercept and then re-raise exception
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
            # Try to intercept and then re-raise exception
            self._try_intercept_user_error(user_error, product_id)

    def _try_intercept_user_error(self, user_error, product_id):
        error = user_error.name
        redirections = self.env["procurement.exception"].search([])
        for redirection in redirections:
            if redirection.user_id and redirection.match(product_id, error):
                self._log_exception(
                    product_id.product_tmpl_id, error, redirection.user_id
                )
                # Stop after first match
                break
        # We can finally re-raise UserError even if we are possibly in a transaction
        # because exception has been logged using a new database cursor.
        # (note that _log_next_activity implementation from stock.rule
        # also check for an existing activity).
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
                self._log_exception(
                    product_id.product_tmpl_id, error, redirection.user_id
                )
                # Stop after first redirection match
                break

    def _log_exception(self, product_tmpl_id, message, user_id):
        # Create a new cursor to save this exception activity in database
        # even if we are in a transaction that will probably be rolled back
        with self.env.registry.cursor() as cr:
            env0 = api.Environment(cr, self.env.user.id, {})

            # Assign this cursor to self and all arguments to ensure consistent
            # data in all methods
            _self = self.with_env(env0)
            _product_tmpl_id = product_tmpl_id.with_env(env0)
            _user_id = user_id.with_env(env0)

            # Check that this product exists in the database, because it is possible
            # that it was created during the previous uncommited transaction
            if _product_tmpl_id.exists():
                log_to_current_transaction = False
                if _self._log_exception_as_activity(
                    _product_tmpl_id, message, _user_id
                ):
                    # Commit this created activity to keep it even after a rollback
                    cr.commit()
            else:
                log_to_current_transaction = True
        # The product has probably been created in the current transaction, so we also
        # log this exception activity into it
        if log_to_current_transaction:
            self._log_exception_as_activity(product_tmpl_id, message, user_id)

    def _log_exception_as_activity(self, product_tmpl_id, message, user_id):
        # note = tools.plaintext2html(message)
        note = message
        MailActivity = self.env["mail.activity"]
        model_product_template = self.env.ref("product.model_product_template")
        existing_activity = MailActivity.search(
            [
                ("res_id", "=", product_tmpl_id.id),
                ("res_model_id", "=", model_product_template.id),
                ("note", "=", note),
                ("user_id", "=", user_id.id),
            ]
        )
        if not existing_activity:
            # Will be None if this warning activity type has been deleted
            activity_type_id = self.env.ref(
                "mail.mail_activity_data_warning", raise_if_not_found=False
            )
            _logger.info(
                "Creating new exception (Activity): {}: {}".format(
                    product_tmpl_id.display_name,
                    note,
                )
            )
            activity_data = {
                "activity_type_id": activity_type_id and activity_type_id.id or False,
                "note": note,
                "summary": _("Exception"),
                "user_id": user_id.id,
                "res_id": product_tmpl_id.id,
                "res_model_id": model_product_template.id,
            }
            _logger.debug(activity_data)
            MailActivity.create(activity_data)
            return True
        else:
            return False
