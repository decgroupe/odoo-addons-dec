# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def _compute_assigned_resource(self):
        """Fallback assigned resource to team name when no user is set."""
        res = super()._compute_assigned_resource()
        for rec in self.filtered("team_id"):
            if not rec.assigned_resource:
                rec.assigned_resource = rec.team_id.name
        return res
