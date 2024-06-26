# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    default_task_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Default Task's User",
    )

    def action_assign_to_me(self):
        self.write(
            {
                "user_id": self.env.user.id,
            }
        )
