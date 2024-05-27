# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools.config import config, to_list


class SaleOrder(models.Model):
    _inherit = "sale.order"

    locked_draft = fields.Boolean(
        string="Locked",
        copy=False,
        default=False,
        help="Prevent changes by users other than the salesperson",
    )

    same_user = fields.Boolean(
        compute="_compute_same_user",
        readonly=True,
    )

    def action_draft_lock(self):
        for order in self:
            order.locked_draft = True

    def action_draft_unlock(self):
        for order in self:
            order.locked_draft = False

    def write(self, vals):
        self._update_lock_state(vals)
        return super().write(vals)

    def _update_lock_state(self, vals):
        locked_fields = self._get_locked_fields(vals)
        for order in self:
            if order.state == "draft":
                order._check_lock_unlock(vals)
                if (
                    vals.get("state") == "sale"
                    and self.locked_draft
                    and order._can_edit_locked()
                ):
                    vals["locked_draft"] = False
                elif not order._can_edit_locked() and locked_fields:
                    order._check_lock_changes(vals, locked_fields)

    @api.model
    def _get_lockable_fields(self):
        ICP = self.env["ir.config_parameter"].sudo()
        lockable_fields = ICP.get_param("sale_lockable.fields")
        return to_list(lockable_fields)

    @api.model
    def _get_locked_fields(self, vals):
        inter_fields = list(set(self._get_lockable_fields()).intersection(vals))
        if inter_fields:
            locked_fields = self.fields_get(inter_fields)
        else:
            locked_fields = []
        return locked_fields

    def _check_lock_changes(self, vals, fields):
        """Check if someone is trying to modify a locked quotation"""
        self.ensure_one()
        if self.locked_draft and not "locked_draft" in vals:
            translated_fields = [fields[k]["string"] for k in fields]
            raise UserError(
                _("%s is currently locked, you are not allowed to make changes to %s")
                % (self.name, ", ".join(translated_fields))
            )

    def _can_edit_locked(self):
        self.ensure_one()
        res = self.same_user or self.env.user._is_admin() or self.env.su
        return res

    def _check_lock_unlock(self, vals):
        """Check if someone is trying to unlock a quotation"""
        self.ensure_one()
        if "locked_draft" in vals and vals.get("locked_draft") != self.locked_draft:
            if vals.get("locked_draft") and not self.user_id:
                raise UserError(
                    _("A salesperson must be set before locking a sale order")
                )
            if self._can_edit_locked():
                if vals.get("locked_draft"):
                    msg = _("⛔ Locked by {}").format(self.env.user.name)
                else:
                    msg = _("✅ Unlocked by {}").format(self.env.user.name)
                self.message_post(body=msg)
            else:
                raise UserError(
                    _("Only %s or an Administrator can lock/unlock this quotation")
                    % (self.user_id.name)
                )

    @api.depends("user_id")
    @api.depends_context("env.user")
    def _compute_same_user(self):
        for order in self:
            order.same_user = order.user_id == self.env.user
