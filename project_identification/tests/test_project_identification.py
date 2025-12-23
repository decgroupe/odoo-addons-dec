# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

from .common import TestProjectIdentificationBase


class TestProjectIdentification(TestProjectIdentificationBase):
    def setUp(self):
        super().setUp()

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

    def test_03_project_display_name(self):
        self._create_projects()
        self.assertProjectDisplayName(
            self.pA,
            {"name_search": True},
            "ProjectA",
            "ProjectA",
        )
        self.assertProjectDisplayName(
            self.pB,
            {"name_search": True},
            "ProjectB",
            "ProjectB → ⏱️",
        )
        self.assertProjectDisplayName(
            self.pB,
            {"name_search": True},
            "ProjectB",
            "ProjectB → ⏱️",
        )
        self.assertProjectDisplayName(
            self.pC,
            {"name_search": True},
            "ProjectC",
            "ProjectC → 📝 Contract",
        )

    def test_04a_project_name_search(self):
        # search using name
        self._create_projects()
        self.assertProjectNameSearchEqual(
            self.pA,
            "ProjectA",
            "ProjectA",
        )
        self.assertProjectNameSearchEqual(
            self.pB,
            "ProjectB",
            "ProjectB → ⏱️",
        )
        self.assertProjectNameSearchEqual(
            self.pC,
            "ProjectC",
            "ProjectC → 📝 Contract",
        )

    def test_04b_project_name_search(self):
        # search using identification name
        self._create_projects()
        self.assertProjectNameSearchEqual(
            self.pB,
            "ProjectB → ⏱️",
            "ProjectB → ⏱️",
        )
        self.assertProjectNameSearchEqual(
            self.pC,
            "ProjectC → 📝 Contract",
            "ProjectC → 📝 Contract",
        )

    def test_10_task_display_name(self):
        self._create_projects()
        self._create_tasks()

        self.assertTaskDisplayName(
            self.t1,
            {"name_search": True},
            "Task 1",
            "Task 1",
        )
        self.assertTaskDisplayName(
            self.tA1,
            {"name_search": True},
            "Task A1",
            "✨ Task A1",
        )
        self.assertTaskDisplayName(
            self.tB1,
            {"name_search": True},
            "Task B1",
            "✨ Task B1 → ⏱ ProjectB",
        )

        self.assertTaskDisplayName(
            self.tC1,
            {"name_search": True},
            "Task C1",
            "✨ Task C1 → 📝 ProjectC",
        )

    def test_11_task_name_search(self):
        self._create_projects()
        self._create_tasks()
        # search using name
        self.assertTaskNameSearchEqual(
            self.t1,
            "Task 1",
            "Task 1",
        )
        self.assertTaskNameSearchEqual(
            self.tA1,
            "Task A1",
            "✨ Task A1",
        )
        self.assertTaskNameSearchEqual(
            self.tA2,
            "Task A2",
            "🚧 Task A2",
        )
        self.assertTaskNameSearchEqual(
            self.tB1,
            "Task B1",
            "✨ Task B1 → ⏱ ProjectB",
        )
        self.assertTaskNameSearchEqual(
            self.tC1,
            "Task C1",
            "✨ Task C1 → 📝 ProjectC",
        )
        # search using identification name
        self.assertTaskNameSearchEqual(
            self.tB1,
            "Task B1 → ⏱ ProjectB",
            "✨ Task B1 → ⏱ ProjectB",
        )
        self.assertTaskNameSearchEqual(
            self.tB1,
            "✨ Task B1 → ⏱ ProjectB",
            "✨ Task B1 → ⏱ ProjectB",
        )
        self.assertTaskNameSearchEqual(
            self.tC1,
            "Task C1 → 📝 ProjectC",
            "✨ Task C1 → 📝 ProjectC",
        )
        self.assertTaskNameSearchEqual(
            self.tC1,
            "✨ Task C1 → 📝 ProjectC",
            "✨ Task C1 → 📝 ProjectC",
        )
        # searching using symbol but without arrow should fail
        self.assertTaskNameSearchEqual(
            self.tB1,
            "✨ Task B1",
            False,
        )
        self.assertTaskNameSearchEqual(
            self.tB1,
            "✨ Task C1",
            False,
        )
