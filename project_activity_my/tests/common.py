# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from datetime import timedelta

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestProjectActivityMyCommon(TransactionCase):
    """Base class for project_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.Activity = cls.env["mail.activity"]
        cls.user = cls.env.ref("base.user_root")
        cls.user2 = cls.env["res.users"].create(
            {
                "name": "Test User 2",
                "login": "test_user_2_proj_act_my",
                "email": "test2_proj_act_my@test.com",
                "groups_id": [Command.set([cls.env.ref("base.group_user").id])],
            }
        )
        cls.activity_type = cls.env["mail.activity.type"].create(
            {"name": "Test Project My Activity Type"}
        )
        cls.project = cls.Project.create({"name": "Test Project for My Activities"})
        cls.task = cls.Task.create(
            {
                "name": "Test Task for My Activities",
                "project_id": cls.project.id,
            }
        )

    def _make_activity(self, record, user, days_from_today=0):
        """Create a test activity for the given record and user."""
        deadline = fields.Date.today() + timedelta(days=days_from_today)
        model_id = self.env["ir.model"]._get(record._name).id
        return self.Activity.sudo().create(
            {
                "activity_type_id": self.activity_type.id,
                "res_id": record.id,
                "res_model_id": model_id,
                "user_id": user.id,
                "date_deadline": deadline,
            }
        )
