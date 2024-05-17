# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from datetime import datetime

from odoo import SUPERUSER_ID, _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    # Add index to speed-up search
    bom_id = fields.Many2one(index=True)

    stage_id = fields.Many2one(
        comodel_name="mrp.production.stage",
        string="Stage",
        ondelete="set null",
        default=lambda self: self._get_default_stage_id(),
        group_expand="_read_group_stage_ids",
        compute="_compute_stage_id",
        tracking=True,
        index=True,
        store=True,
        copy=False,
    )

    stage_todo = fields.Boolean(
        string="To-do",
        related="stage_id.todo",
        help="Used as a filter to only display production order linked to "
        "stages with to-do actions",
        index=True,
        store=True,
    )

    # For Kanban
    kanban_color = fields.Integer(string="Color Index")

    # Used for Kanban grouped_by view
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env["mrp.production.stage"].search([])
        return stages or stage_ids

    def _get_default_stage_id(self):
        """Gives default stage_id"""
        return self.env.ref("mrp_stage.stage_confirmed", raise_if_not_found=False)

    @api.model
    def _get_stages_ref(self):
        return {
            "draft": self.env.ref("mrp_stage.stage_draft"),
            "confirmed": self.env.ref("mrp_stage.stage_confirmed"),
            "progress": self.env.ref("mrp_stage.stage_progress"),
            "issue": self.env.ref("mrp_stage.stage_issue"),
            "dispatch_ready": self.env.ref("mrp_stage.stage_dispatch_ready"),
            "to_close": self.env.ref("mrp_stage.stage_done"),
            "done": self.env.ref("mrp_stage.stage_done"),
            "cancel": self.env.ref("mrp_stage.stage_cancel"),
        }

    def _get_stage_from_activity(self):
        self.ensure_one()
        activity_ids = self.activity_ids
        res = False
        for activity_id in activity_ids:
            if activity_id.activity_type_id.production_stage_id:
                seq = activity_id.activity_type_id.production_stage_id.sequence
                if not res or seq > res.sequence:
                    res = activity_id.activity_type_id
        if res:
            res = res.production_stage_id
        return res

    def _get_stage_from_state(self, stages):
        self.ensure_one()
        stage_id = False
        if self.state in stages:
            stage_id = stages[self.state]
        elif self.state == "to_close":
            stage_id = stages["progress"]
        if self.state in ("confirmed", "progress", "to_close"):
            activity_stage_id = self._get_stage_from_activity()
            if activity_stage_id:
                stage_id = activity_stage_id
        elif self.state in ("done"):
            move_finished_ids = self.move_finished_ids.filtered(
                lambda x: x.state in ("done", "cancel")
            )
            picking_move_ids = move_finished_ids.mapped("move_dest_ids")
            if not all(m.state in ("done", "cancel") for m in picking_move_ids):
                stage_id = stages["dispatch_ready"]
        return stage_id

    @api.depends(
        "state",
        "activity_ids",
        "activity_ids.state",
        "move_finished_ids.move_dest_ids.state",
    )
    def _compute_stage_id(self):
        self.stage_id = False
        if self.env.context.get("module") == "mrp_stage":
            return
        stages = self._get_stages_ref()
        for rec in self:
            stage_id = rec._get_stage_from_state(stages)
            if stage_id:
                rec.stage_id = stage_id

    def action_recompute_stage_id(self):
        self._compute_stage_id()

    def action_assign_to_me(self):
        self.write(
            {
                "user_id": self.env.user.id,
            }
        )

    def action_start(self):
        self.ensure_one()
        if self.state in ("done", "cancel"):
            return True
        self.write(
            {
                "state": "progress",
                "date_start": datetime.now(),
            }
        )
        # OCA module needed: web_ir_actions_act_view_reload
        return {
            "type": "ir.actions.act_view_reload",
        }

    def action_on_hold(self):
        self.ensure_one()
        if self.state in ("draft", "done", "cancel"):
            return True
        self.write(
            {
                "state": "confirmed",
            }
        )
        # OCA module needed: web_ir_actions_act_view_reload
        return {
            "type": "ir.actions.act_view_reload",
        }

    def _allow_auto_start(self):
        self.ensure_one()
        return self.state in ("confirmed")

    def action_view_staged(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_stage.act_mrp_production_staged"
        )
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            action["views"] = [
                (self.env.ref("mrp.mrp_production_form_view").id, "form")
            ]
            action["res_id"] = self.id
        return action

    @api.model
    def action_view_staged_with_products(self, product_ids):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_stage.act_mrp_production_staged"
        )
        action["domain"] = [("product_id", "in", product_ids)]
        action["context"] = {}
        return action
