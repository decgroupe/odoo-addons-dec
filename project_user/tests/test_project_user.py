# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.tests.common import Form


class TestProjectUser(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project_model = self.env["project.project"]
        self.task_model = self.env["project.task"]
        self.user_root = self.env.ref("base.user_root")
        self.user_admin = self.env.ref("base.user_admin")
        self.company_admin = self.user_admin.company_id
        self.user_jasmine = mail_new_test_user(
            self.env,
            login="jasmine",
            groups="project.group_project_user",
            company_id=self.company_admin.id,
            name="Jasmine",
            email="jasmine@test.example.com",
            notification_type="inbox",
            signature="--\nJasmine",
        )

    def test_01_default_task_user(self):
        project_id = self.env.ref("project.project_project_1")
        project_id.default_task_user_id = self.user_jasmine
        task_form = Form(self.task_model.with_context(default_project_id=project_id.id))
        self.assertEqual(task_form.project_id, project_id)
        self.assertEqual(task_form.user_id, self.user_jasmine)
        task_form.name = "A new task"
        task_id = task_form.save()
        self.assertEqual(task_id.project_id, project_id)
        self.assertEqual(task_id.user_id, self.user_jasmine)

    def test_02_project_assign_to_me(self):
        project_id = self.env.ref("project.project_project_1")
        project_id.action_assign_to_me()
        self.assertEqual(project_id.user_id, self.user_root)
        project_id.with_user(self.user_admin).action_assign_to_me()
        self.assertEqual(project_id.user_id, self.user_admin)
        with self.assertRaisesRegex(
            AccessError,
            r"You are not allowed to modify 'Project' \(project.project\) records",
        ):
            project_id.with_user(self.user_jasmine).action_assign_to_me()

    def test_03_task_assign_to_me(self):
        task_id = self.env.ref("project.project_task_6")
        self.assertEqual(task_id.user_id, self.user_admin)
        task_id.action_assign_to_me()
        self.assertEqual(task_id.user_id, self.user_root)
        task_id.with_user(self.user_jasmine).action_assign_to_me()
        self.assertEqual(task_id.user_id, self.user_jasmine)
