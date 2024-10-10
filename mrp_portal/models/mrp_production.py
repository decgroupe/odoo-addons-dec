# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024


import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError


def _checksum(value):
    digits = [int(d) for d in str(value)]
    res = digits[0]
    for v in digits[1:]:
        res = (res << 1) ^ v
    return res % 255


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    identifier = fields.Char(
        compute="_compute_identifier",
        store=True,
    )
    identifier_checksum = fields.Integer(
        compute="_compute_identifier",
        store=True,
    )

    @api.depends("name")
    def _compute_identifier(self):
        for rec in self:
            rec.identifier = re.sub("[^0-9]", "", rec.name)
            if rec.identifier:
                rec.identifier_checksum = _checksum(rec.identifier)
            else:
                rec.identifier_checksum = -1

    def _get_action_type_xmlid(self, action):
        if action == "close":
            return "mrp_portal.mail_act_notification_close"
        elif action == "cancel":
            return "mrp_portal.mail_act_notification_cancel"
        else:
            raise Exception("Action must be in close or cancel")

    def _get_activity_user(self):
        self.ensure_one()
        user_id = self.user_id
        reason = _("This user is assigned to this production order")
        return user_id, reason

    def _create_activity(self, action, user_id):
        self.ensure_one()
        act_type_xmlid = self._get_action_type_xmlid(action)
        return self.with_context(
            mail_activity_noautofollow=True,
        ).activity_schedule(
            act_type_xmlid=act_type_xmlid,
            note=_("🚨 Auto: To Process"),
            user_id=user_id.id,
        )

    def _get_activity(self, action):
        self.ensure_one()
        act_type_xmlid = self._get_action_type_xmlid(action)
        act_type_xmlid = self.env.ref(act_type_xmlid)
        domain = [
            ("id", "in", self.activity_ids.ids),
            ("activity_type_id", "=", act_type_xmlid.id),
        ]
        activity_id = self.env["mail.activity"].search(domain)
        return activity_id

    def _delete_activity(self, action):
        self.ensure_one()
        activity_id = self._get_activity(action)
        # only close activity if there is one and only one
        if len(activity_id) == 1:
            activity_id.unlink()

    def _remote_update_producing_quantity(self, qty, ip_addr):
        self.ensure_one()
        if self.qty_producing != qty:
            self.message_post_with_view(
                views_or_xmlid=f"mrp_portal.production_update_producing_quantity",
                values={
                    "ip_addr": ip_addr,
                    "old_value": self.qty_producing,
                    "new_value": qty,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
            self.qty_producing = qty
            self._set_qty_producing()

    def _remote_notify(self, action, ip_addr):
        self.ensure_one()
        self.message_post_with_view(
            views_or_xmlid=f"mrp_portal.production_notify_{action}",
            values={
                "ip_addr": ip_addr,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        # recreate default activity if needed
        activity_id = self._get_activity(action)
        if not activity_id:
            user_id, _user_assigned_reason = self._get_activity_user()
            if user_id:
                activity_id = self._create_activity(action, user_id)
        return activity_id

    def _delete_notify_activities(self):
        self._delete_activity("close")
        self._delete_activity("cancel")

    def _remote_notify_done(self, ip_addr):
        self._delete_notify_activities()
        self._remote_notify("close", ip_addr)

    def _remote_notify_cancel(self, ip_addr):
        self._delete_notify_activities()
        self._remote_notify("cancel", ip_addr)
