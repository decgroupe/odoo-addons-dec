# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

import logging

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestProjectIdentificationBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_project = cls.env["project.project"]
        cls.model_task = cls.env["project.task"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user = new_test_user(
            cls.env,
            login="project_identification-user",
            groups="base.group_user",
            context=ctx,
        )
        cls.ptype_time_tracking = cls.env.ref(
            "project_identification.time_tracking_type"
        )
        cls.ptype_contract = cls.env.ref("project_identification.contract_type")
        cls.task_stage_new = cls.env.ref("project.project_stage_0")
        cls.task_stage_new.name = "✨ New"
        cls.task_stage_progress = cls.env.ref("project.project_stage_1")
        cls.task_stage_progress.name = "🚧 Progress"

    def setUp(self):
        super().setUp()

    def _create_projects(self, context=None):
        if context is None:
            context = {}
        self.pA = self.model_project.with_context(**context).create(
            {"name": "ProjectA", "type_id": False},
        )
        self.pB = self.model_project.with_context(**context).create(
            {"name": "ProjectB", "type_id": self.ptype_time_tracking.id},
        )
        self.pC = self.model_project.with_context(**context).create(
            {"name": "ProjectC", "type_id": self.ptype_contract.id},
        )

    def _create_tasks(self):
        self.t1 = self.model_task.create(
            {
                "name": "Task 1",
                "project_id": False,
            }
        )
        self.tA1 = self.model_task.create(
            {
                "name": "Task A1",
                "project_id": self.pA.id,
                "stage_id": self.task_stage_new.id,
            }
        )
        self.tA2 = self.model_task.create(
            {
                "name": "Task A2",
                "project_id": self.pA.id,
                "stage_id": self.task_stage_progress.id,
            }
        )
        self.tB1 = self.model_task.create(
            {
                "name": "Task B1",
                "project_id": self.pB.id,
                "stage_id": self.task_stage_new.id,
            }
        )
        self.tB2 = self.model_task.create(
            {
                "name": "Task B2",
                "project_id": self.pB.id,
                "stage_id": self.task_stage_progress.id,
            }
        )
        self.tC1 = self.model_task.create(
            {
                "name": "Task C1",
                "project_id": self.pC.id,
                "stage_id": self.task_stage_new.id,
            }
        )
        self.tC2 = self.model_task.create(
            {
                "name": "Task C2",
                "project_id": self.pC.id,
                "stage_id": self.task_stage_progress.id,
            }
        )

    def assertProjectNameSearchEqual(self, project, name, expected_result):
        self.model_project.invalidate_model(["display_name"])
        res = self.model_project.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], project.id)
            self.assertEqual(res[0][1], expected_result)
        except IndexError:
            self.fail(
                f"Expected to find a project with name_search '{name}' "
                f"but found {res}.\n"
                f"Project is '{project.display_name}'"
            )

    def assertProjectDisplayName(
        self, project, context, normal_name, identification_name
    ):
        self.model_project.invalidate_model(["display_name"])
        self.assertEqual(project.display_name, normal_name)
        self.model_project.invalidate_model(["display_name"])
        self.assertEqual(
            project.with_context(**context).display_name, identification_name
        )

    def assertTaskNameSearchEqual(self, task, name, expected_result):
        self.model_task.invalidate_model(["display_name"])
        res = self.model_task.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], task.id)
            self.assertEqual(res[0][1], expected_result)
        except IndexError:
            self.fail(
                f"Expected to find a task with name_search '{name}' "
                f"but found {res}.\n"
                f"Task is '{task.display_name}'"
            )

    def assertTaskDisplayName(self, task, context, normal_name, identification_name):
        self.model_task.invalidate_model(["display_name"])
        self.assertEqual(task.display_name, normal_name)
        self.model_task.invalidate_model(["display_name"])
        self.assertEqual(task.with_context(**context).display_name, identification_name)
