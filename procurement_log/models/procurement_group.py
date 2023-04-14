# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

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
