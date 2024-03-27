# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import fields, models


class MergeTask(models.TransientModel):
    _inherit = "merge.object.wizard"
    _name = "merge.project.task.wizard"
    _description = "Merge Task Wizard"
    _model_merge = "project.task"
    _table_merge = "project_task"

    object_ids = fields.Many2many(
        comodel_name=_model_merge,
        string="Task",
    )
    dst_object_id = fields.Many2one(
        comodel_name=_model_merge,
        string="Task",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="dst_object_id.company_id",
        string="Company",
        readonly=True,
        default=lambda self: self.env.user.company_id,
    )

    def _merge(self, object_ids, dst_object=None, extra_checks=True):
        return super()._merge(
            object_ids,
            dst_object.with_context(mail_auto_subscribe_no_notify=True),
            extra_checks,
        )

    def _log_merge_operation(self, src_objects, dst_object):
        super()._log_merge_operation(src_objects, dst_object)
        template_id = self.env.ref("project_merge.merged_tasks")
        for src_object in src_objects:
            partner_id = src_object.user_id.mapped("partner_id")
            if partner_id:
                partner_to = ",".join(str(id) for id in partner_id.ids)
            else:
                partner_to = False
            # do not use force_send because the merge can fail and we don't want send
            # a false e-mail
            template_id.with_context(
                src_object=src_object, partner_to=partner_to
            ).send_mail(self.id, force_send=False)
