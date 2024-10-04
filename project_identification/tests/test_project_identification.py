# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestProjectIdentification(SavepointCase):

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
        self.pA = self.model_project.with_context(context).create(
            {"name": "ProjectA", "type_id": False},
        )
        self.pB = self.model_project.with_context(context).create(
            {"name": "ProjectB", "type_id": self.ptype_time_tracking.id},
        )
        self.pC = self.model_project.with_context(context).create(
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

    def test_01_project_is_type(self):
        self._create_projects()
        self.assertFalse(self.pA.is_contract)
        self.assertFalse(self.pA.is_time_tracking)
        self.assertFalse(self.pB.is_contract)
        self.assertTrue(self.pB.is_time_tracking)
        self.assertTrue(self.pC.is_contract)
        self.assertFalse(self.pC.is_time_tracking)

    def test_02_project_type_at_module_installation(self):
        self._create_projects(context={"module": "project_identification"})
        self.assertFalse(self.pA.is_contract)
        self.assertFalse(self.pA.is_time_tracking)
        self.assertFalse(self.pB.is_contract)
        self.assertFalse(self.pB.is_time_tracking)
        self.assertFalse(self.pC.is_contract)
        self.assertFalse(self.pC.is_time_tracking)

    def test_03_project_name_get(self):
        self._create_projects()
        self.assertEqual(self.pA.name_get()[0][1], "ProjectA")
        self.assertEqual(self.pB.name_get()[0][1], "ProjectB")
        self.assertEqual(self.pC.name_get()[0][1], "ProjectC")
        self.assertEqual(
            self.pA.with_context(name_search=True).name_get()[0][1],
            "ProjectA",
        )
        self.assertEqual(
            self.pB.with_context(name_search=True).name_get()[0][1],
            "ProjectB → ⏱️",
        )
        self.assertEqual(
            self.pC.with_context(name_search=True).name_get()[0][1],
            "ProjectC → 📝 Contract",
        )

    def test_04_project_name_search(self):
        self._create_projects()
        # search using name
        res = self.model_project.name_search(name="ProjectA")
        self.assertEqual(res[0][0], self.pA.id)
        self.assertEqual(res[0][1], "ProjectA")
        res = self.model_project.name_search(name="ProjectB")
        self.assertEqual(res[0][0], self.pB.id)
        self.assertEqual(res[0][1], "ProjectB → ⏱️")
        res = self.model_project.name_search(name="ProjectC")
        self.assertEqual(res[0][0], self.pC.id)
        self.assertEqual(res[0][1], "ProjectC → 📝 Contract")
        # search using identification name
        res = self.model_project.name_search(name="ProjectB → ⏱️")
        self.assertEqual(res[0][0], self.pB.id)
        self.assertEqual(res[0][1], "ProjectB → ⏱️")
        res = self.model_project.name_search(name="ProjectC → 📝 Contract")
        self.assertEqual(res[0][0], self.pC.id)
        self.assertEqual(res[0][1], "ProjectC → 📝 Contract")

    def test_10_task_name_get(self):
        self._create_projects()
        self._create_tasks()
        self.assertEqual(self.t1.name_get()[0][1], "Task 1")
        self.assertEqual(self.tA1.name_get()[0][1], "Task A1")
        self.assertEqual(self.tB1.name_get()[0][1], "Task B1")
        self.assertEqual(self.tC1.name_get()[0][1], "Task C1")
        self.assertEqual(
            self.t1.with_context(name_search=True).name_get()[0][1],
            "Task 1",
        )
        self.assertEqual(
            self.tA1.with_context(name_search=True).name_get()[0][1],
            "✨ Task A1",
        )
        self.assertEqual(
            self.tB1.with_context(name_search=True).name_get()[0][1],
            "✨ Task B1 → ⏱ ProjectB",
        )
        self.assertEqual(
            self.tC1.with_context(name_search=True).name_get()[0][1],
            "✨ Task C1 → 📝 ProjectC",
        )

    def test_11_task_name_search(self):
        self._create_projects()
        self._create_tasks()
        # search using name
        res = self.model_task.name_search(name="Task 1")
        self.assertEqual(res[0][0], self.t1.id)
        self.assertEqual(res[0][1], "Task 1")
        res = self.model_task.name_search(name="Task A1")
        self.assertEqual(res[0][0], self.tA1.id)
        self.assertEqual(res[0][1], "✨ Task A1")
        res = self.model_task.name_search(name="Task A2")
        self.assertEqual(res[0][0], self.tA2.id)
        self.assertEqual(res[0][1], "🚧 Task A2")
        res = self.model_task.name_search(name="Task B1")
        self.assertEqual(res[0][0], self.tB1.id)
        self.assertEqual(res[0][1], "✨ Task B1 → ⏱ ProjectB")
        res = self.model_task.name_search(name="Task C1")
        self.assertEqual(res[0][0], self.tC1.id)
        self.assertEqual(res[0][1], "✨ Task C1 → 📝 ProjectC")
        # search using identification name
        res = self.model_task.name_search(name="Task B1 → ⏱ ProjectB")
        self.assertEqual(res[0][0], self.tB1.id)
        self.assertEqual(res[0][1], "✨ Task B1 → ⏱ ProjectB")
        res = self.model_task.name_search(name="✨ Task B1 → ⏱ ProjectB")
        self.assertEqual(res[0][0], self.tB1.id)
        self.assertEqual(res[0][1], "✨ Task B1 → ⏱ ProjectB")
        res = self.model_task.name_search(name="Task C1 → 📝 ProjectC")
        self.assertEqual(res[0][0], self.tC1.id)
        self.assertEqual(res[0][1], "✨ Task C1 → 📝 ProjectC")
        res = self.model_task.name_search(name="✨ Task C1 → 📝 ProjectC")
        self.assertEqual(res[0][0], self.tC1.id)
        self.assertEqual(res[0][1], "✨ Task C1 → 📝 ProjectC")
        # searching using emoji but without arrow should fail
        res = self.model_task.name_search(name="✨ Task B1")
        self.assertFalse(res)
        res = self.model_task.name_search(name="✨ Task C1")
        self.assertFalse(res)
