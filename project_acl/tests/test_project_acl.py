# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError


class TestProjectAcl(SavepointCase):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_model = cls.env["project.project"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.project_user = new_test_user(
            cls.env,
            login="project_acl-project_user",
            groups="project.group_project_user",
            context=ctx,
        )
        cls.project_manager = new_test_user(
            cls.env,
            login="project_acl-project_manager",
            groups="project.group_project_manager",
            context=ctx,
        )
        cls.project_supermanager = new_test_user(
            cls.env,
            login="project_acl-project_supermanager",
            groups="project_acl.group_project_supermanager",
            context=ctx,
        )

    def test_01_create_project_as_project_user(self):
        with self.assertRaisesRegex(AccessError, r"Super-Manager"):
            project_id = self.project_model.with_user(self.project_user).create(
                {"name": "project1"}
            )
        # in bypass mode, the standard access error should be raised because a project
        # user do not have rights to create projects
        with self.assertRaisesRegex(AccessError, r"Project\/Administrator"):
            project_id = (
                self.project_model.with_user(self.project_user)
                .with_context(bypass_supermanager_check=True)
                .create({"name": "project1"})
            )
            self.assertTrue(project_id)

    def test_02_create_project_as_project_manager(self):
        with self.assertRaisesRegex(AccessError, r"Super-Manager"):
            project_id = self.project_model.with_user(self.project_manager).create(
                {"name": "project1"}
            )
        project_id = (
            self.project_model.with_user(self.project_manager)
            .with_context(bypass_supermanager_check=True)
            .create({"name": "project1"})
        )
        self.assertTrue(project_id)

    def test_03_create_project_as_project_supermanager(self):
        project1_id = self.project_model.with_user(self.project_supermanager).create(
            {"name": "project1"}
        )
        self.assertTrue(project1_id)

    def test_04_create_project_as_project_supermanager_with_bypass(self):
        project2_id = (
            self.project_model.with_user(self.project_supermanager)
            .with_context(bypass_supermanager_check=True)
            .create({"name": "project2"})
        )
        self.assertTrue(project2_id)
