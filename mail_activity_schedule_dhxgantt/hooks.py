# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

import logging

_logger = logging.getLogger(__name__)

MODULE = "web_dhxgantt"


def uninstall_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    """
    This uninstall-hook will remove dhxgantt from the action.
    """
    env = api.Environment(cr, SUPERUSER_ID, dict())

    # task_action_id = env.ref("project.act_project_project_2_project_task_all")
    # task_action_id.view_mode = 'kanban,tree,form,calendar,pivot,graph,activity'


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    action = env.ref("mail_activity_board.open_boards_activities")
