# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    project_ids = env["project.project"].search([])
    project_ids.with_context(
        mail_activity_quick_update=True,
        tracking_disable=True,
    ).filtered("schedulable")._ensure_scheduling_activity()

    task_ids = env["project.project"].search([])
    task_ids.with_context(
        mail_activity_quick_update=True,
        tracking_disable=True,
    ).filtered("schedulable")._ensure_scheduling_activity()
