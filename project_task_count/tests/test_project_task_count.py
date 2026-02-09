# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProjectTaskCount(TransactionCase):
    def setUp(self):
        super().setUp()

        # create 4 projects with different numbers of open tasks
        self.project_1 = self.env["project.project"].create({"name": "Project 1"})
        self.project_2 = self.env["project.project"].create(
            {
                "name": "Project 2",
                "task_ids": [
                    Command.create({"name": "Task 1"}),
                    Command.create({"name": "Task 2"}),
                ],
            }
        )
        self.project_3 = self.env["project.project"].create(
            {
                "name": "Project 3",
                "task_ids": [
                    Command.create({"name": "Task 3"}),
                    Command.create({"name": "Task 4", "state": "1_done"}),
                ],
            }
        )
        self.project_4 = self.env["project.project"].create(
            {
                "name": "Project 4",
                "task_ids": [
                    Command.create({"name": "Task 5", "state": "1_done"}),
                    Command.create({"name": "Task 6", "state": "1_done"}),
                ],
            }
        )
        # reference to time-tracking task type
        self.time_tracking_type = self.env.ref(
            "project_identification.time_tracking_type"
        )

    def test_01_task_count(self):
        self.assertEqual(
            self.project_1.todo_task_count, 0, "Project 1 should have 0 open tasks"
        )
        self.assertEqual(
            self.project_2.todo_task_count, 2, "Project 2 should have 2 open tasks"
        )
        self.assertEqual(
            self.project_3.todo_task_count, 1, "Project 3 should have 1 open task"
        )
        self.assertEqual(
            self.project_4.todo_task_count, 0, "Project 4 should have 0 open tasks"
        )

    def test_02_task_count_update(self):
        # close one task in project 2
        self.project_2.task_ids[0].state = "1_done"
        self.assertEqual(
            self.project_2.todo_task_count,
            1,
            "Project 2 should have 1 open task after closing one",
        )
        # reopen the same task
        self.project_2.task_ids[0].state = "01_in_progress"
        self.assertEqual(
            self.project_2.todo_task_count,
            2,
            "Project 2 should have 2 open tasks after reopening the task",
        )
        # cancel the same task
        self.project_2.task_ids[0].state = "1_canceled"
        self.assertEqual(
            self.project_2.todo_task_count,
            1,
            "Project 2 should have 1 open task after canceling the task",
        )

    def test_03_task_count_new_task(self):
        # add a new task to project 1
        self.project_1.task_ids = [
            Command.create({"name": "New Task"}),
        ]
        self.assertEqual(
            self.project_1.todo_task_count, 1, "Project 1 should have 1 open task"
        )
        # add a new closed task to project 1
        self.project_1.task_ids = [
            Command.create({"name": "New Task 2", "state": "1_done"}),
        ]
        self.assertEqual(
            self.project_1.todo_task_count, 1, "Project 1 should still have 1 open task"
        )

    def test_04_task_count_time_tracking(self):
        # add a new time-tracking task to project 3
        self.project_3.task_ids = [
            Command.create(
                {
                    "name": "Time Tracking Task",
                    "type_id": self.time_tracking_type.id,
                }
            ),
        ]
        task_id = self.project_3.task_ids[-1]
        self.assertEqual(task_id.name, "Time Tracking Task")
        self.assertEqual(
            self.project_3.todo_task_count,
            1,
            "Project 3 should still have 1 open task "
            "(time-tracking tasks should be excluded)",
        )
        # remove the time-tracking type from newly added task to make it a normal task
        task_id.type_id = False
        self.assertEqual(
            self.project_3.todo_task_count,
            2,
            "Project 3 should have 2 open tasks after removing time-tracking type",
        )
