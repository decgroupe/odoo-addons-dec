# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2021

from odoo import models


class Task(models.Model):
    _inherit = "project.task"

    def get_access_link(self):
        # _notify_get_action_link is not callable from email template
        return self._notify_get_action_link('view')
