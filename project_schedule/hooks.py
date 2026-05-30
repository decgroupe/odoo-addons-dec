# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022


def post_init_hook(env):
    """Create and synchronize scheduling activities for existing records."""
    project_ids = env["project.project"].search([])
    project_ids.with_context(
        mail_activity_quick_update=True,
        tracking_disable=True,
    ).filtered("schedulable")._ensure_scheduling_activity()

    task_ids = env["project.task"].search([])
    task_ids.with_context(
        mail_activity_quick_update=True,
        tracking_disable=True,
    ).filtered("schedulable")._ensure_scheduling_activity()
