# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import _, fields, models
from odoo.exceptions import AccessDenied


class MergeHelpdeskTicket(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.helpdesk.ticket.wizard"
    _description = "Merge Helpdesk Ticket Wizard"
    _model_merge = "helpdesk.ticket"
    _table_merge = "helpdesk_ticket"

    object_ids = fields.Many2many(
        comodel_name=_model_merge,
        string="Helpdesk Ticket",
    )
    dst_object_id = fields.Many2one(
        comodel_name=_model_merge,
        string="Helpdesk Ticket",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="dst_object_id.company_id",
        string="Company",
        readonly=True,
        default=lambda self: self.env.user.company_id,
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        if not self.env.user.has_group("helpdesk_merge.res_group_do_merge"):
            raise AccessDenied(
                _(
                    "You don't have the right to merge tickets. "
                    "Please contact an Administrator."
                )
            )
        return super()._merge(
            object_ids,
            dst_object.with_context(mail_auto_subscribe_no_notify=True),
            extra_checks,
        )

    def _delete_source_objects(self, src_objects):
        return super()._delete_source_objects(src_objects.sudo())
