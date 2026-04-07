# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import contextlib
from unittest.mock import Mock

import odoo
from odoo.tests.common import TransactionCase
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockDebugRequest(env):
    """Simulate a debug HTTP request so base.group_no_one is active."""
    request = Mock(
        db=None,
        env=env,
        session=DotDict(debug=True),
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        s.callback(odoo.http._request_stack.pop)
        yield request


class TestHrTimesheetExcludeCommon(TransactionCase):
    """Base test class for hr_timesheet_exclude module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.AnalyticLine = cls.env["account.analytic.line"]
        cls.employee = cls.env.ref("hr.employee_admin")
        cls.project = cls.Project.create(
            {
                "name": "Test Project",
            }
        )
        cls.task = cls.Task.create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )
