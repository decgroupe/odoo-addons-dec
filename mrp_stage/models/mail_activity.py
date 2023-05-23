# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022


from odoo import models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_done(self):
        super().action_done()
        # OCA modules needed:
        # - web_ir_actions_act_view_reload
        # - web_ir_actions_act_multi
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }

    def action_close_dialog(self):
        super().action_close_dialog()
        # OCA modules needed:
        # - web_ir_actions_act_view_reload
        # - web_ir_actions_act_multi
        return {
            "type": "ir.actions.act_multi",
            "actions": [
                {"type": "ir.actions.act_window_close"},
                {"type": "ir.actions.act_view_reload"},
            ],
        }

    # def unlink(self):
    #     ids = []
    #     ProductionModel = self.env.ref("mrp.model_mrp_production")
    #     for activity in self:
    #         if activity.res_model_id == ProductionModel:
    #             ids.append(activity.res_id)
    #     res = super(MailActivity, self.sudo()).unlink()
    #     if ids:
    #         self.env["mrp.production"].browse(ids).action_recompute_stage_id()
    #     return res
