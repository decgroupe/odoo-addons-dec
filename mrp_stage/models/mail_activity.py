# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

import logging
from odoo import models, api


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def action_close_dialog(self):
        super().action_close_dialog()
        # OCA modules needed:
        # - web_ir_actions_act_view_reload
        # - web_ir_actions_act_multi
        return {
            'type':
                'ir.actions.act_multi',
            'actions':
                [
                    {
                        'type': 'ir.actions.act_window_close'
                    },
                    {
                        'type': 'ir.actions.act_view_reload'
                    },
                ]
        }
