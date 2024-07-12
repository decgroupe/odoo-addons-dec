# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    unique_identifier = fields.Char(string="Unique Identifier")

    def _get_activity_user(self):
        self.ensure_one()
        user_id = self.user_id
        reason = _("This user is assigned to this maintenance request")
        if not user_id and self.maintenance_team_id:
            user_id = self.maintenance_team_id.user_id
            reason = _(
                "This user is the leader of the team assigned to this "
                "maintenance request"
            )
        if not user_id and self.equipment_id:
            user_id = self.equipment_id.technician_user_id
            reason = _(
                "This user is the technician assigned to the equipment of this "
                "maintenance request"
            )
            if not user_id and self.equipment_id.maintenance_team_id:
                user_id = self.equipment_id.maintenance_team_id.user_id
                reason = _(
                    "This user is the leader of the team assigned to the equipment "
                    "of this maintenance request"
                )
        return user_id, reason

    def _create_default_activity(self, user_id):
        self.ensure_one()
        self.with_context(
            mail_activity_noautofollow=True,
        ).activity_schedule(
            act_type_xmlid="maintenance.mail_act_maintenance_request",
            note=_("🚨 Auto: To Process"),
            user_id=user_id.id,
        )

    def _get_default_activity(self):
        self.ensure_one()
        act_type_xmlid = self.env.ref("maintenance.mail_act_maintenance_request")
        domain = [
            ("id", "in", self.activity_ids.ids),
            ("activity_type_id", "=", act_type_xmlid.id),
        ]
        activity_id = self.env["mail.activity"].search(domain)
        return activity_id

    def _close_default_activity(self):
        self.ensure_one()
        activity_id = self._get_default_activity()
        # only close activity if there is one and only one
        if len(activity_id) == 1:
            activity_id.unlink()

    @api.model
    def _remote_create(self, equipment_serial, unique_identifier, data, ip_addr):
        equipment_id = self.env["maintenance.equipment"].search(
            [("serial_no", "=", equipment_serial)], limit=1
        )
        if not equipment_id:
            raise UserError(
                _(
                    "Equipment with serial %(equipment_serial)s not found",
                    equipment_serial=equipment_serial,
                )
            )
        request_id = self.create(
            {
                "name": data.get("name"),
                "unique_identifier": unique_identifier,
                "equipment_id": equipment_id.id,
                "maintenance_type": data.get("maintenance_type"),
                "description": data.get("description"),
                "priority": data.get("priority"),
            }
        )
        user_id, user_assigned_reason = request_id._get_activity_user()
        if user_id:
            if user_id != request_id.user_id:
                request_id.user_id = user_id
            request_id._create_default_activity(user_id)
        request_id.message_post_with_view(
            views_or_xmlid="maintenance_portal.request_create",
            values={
                "ip_addr": ip_addr,
                "user": user_id,
                "assigned_reason": user_assigned_reason,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return request_id

    def _remote_update(self, data, ip_addr):
        self.ensure_one()
        updated_data = {}
        for key in data:
            if data[key] != self[key]:
                updated_data[key] = data[key]
        if updated_data:
            self.update(data)
            self.message_post_with_view(
                views_or_xmlid="maintenance_portal.request_update",
                values={
                    "ip_addr": ip_addr,
                    "data": updated_data,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
        else:
            self.message_post_with_view(
                views_or_xmlid="maintenance_portal.request_ping",
                values={
                    "ip_addr": ip_addr,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
        # recreate default activity if needed
        activity_id = self._get_default_activity()
        if not activity_id:
            user_id, _user_assigned_reason = self._get_activity_user()
            if user_id:
                self._create_default_activity(user_id)

    def _remote_close(self, data, ip_addr):
        self.ensure_one()
        post_values = {
            "ip_addr": ip_addr,
        }
        if data.get("closed_reason"):
            post_values["closed_reason"] = data.get("closed_reason")
        self.message_post_with_view(
            views_or_xmlid="maintenance_portal.request_close",
            values=post_values,
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        # not needed since odoo delete all activities on archived documents
        self._close_default_activity()
        self.archive_equipment_request()
