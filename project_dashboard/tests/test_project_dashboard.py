# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestProjectDashboard(TransactionCase):
    def setUp(self):
        super().setUp()
        # references to demo data (project types)
        self.type_a = self.env.ref("project_dashboard.project_type_a")
        self.type_b = self.env.ref("project_dashboard.project_type_b")
        self.type_c = self.env.ref("project_dashboard.project_type_c")
        # references to demo data (projects)
        self.project_a_0 = self.env.ref("project_dashboard.project_a_0")
        self.project_a_1 = self.env.ref("project_dashboard.project_a_1")
        self.project_a_2 = self.env.ref("project_dashboard.project_a_2")
        self.project_a_3 = self.env.ref("project_dashboard.project_a_3")
        self.project_a_4 = self.env.ref("project_dashboard.project_a_4")
        self.project_b_0 = self.env.ref("project_dashboard.project_b_0")
        self.project_b_1 = self.env.ref("project_dashboard.project_b_1")
        self.project_b_2 = self.env.ref("project_dashboard.project_b_2")
        self.project_b_3 = self.env.ref("project_dashboard.project_b_3")
        self.project_c_0 = self.env.ref("project_dashboard.project_c_0")
        self.project_c_1 = self.env.ref("project_dashboard.project_c_1")
        self.project_c_2 = self.env.ref("project_dashboard.project_c_2")

    def test_01_ensure_default_data(self):
        # type A
        self.type_a.todo_project_count = 5
        self.type_a.todo_project_count_unassigned = 1
        self.type_a.todo_project_count_year_nm0 = 1
        self.type_a.todo_project_count_year_nm1 = 1
        self.type_a.todo_project_count_year_nm2 = 3
        # type B
        self.type_b.todo_project_count = 4
        self.type_b.todo_project_count_unassigned = 0
        self.type_b.todo_project_count_year_nm0 = 1
        self.type_b.todo_project_count_year_nm1 = 2
        self.type_b.todo_project_count_year_nm2 = 1
        # type C
        self.type_c.todo_project_count = 3
        self.type_c.todo_project_count_unassigned = 0
        self.type_c.todo_project_count_year_nm0 = 0
        self.type_c.todo_project_count_year_nm1 = 1
        self.type_c.todo_project_count_year_nm2 = 2

    def test_02_dashboard_data(self):
        types = self.type_a + self.type_b + self.type_c
        data = types._get_dashboard_data()
        type_ids = [k for k in data.keys()]
        self.assertIn(self.type_a.id, type_ids)
        self.assertIn(self.type_b.id, type_ids)
        self.assertIn(self.type_c.id, type_ids)
        # validate type A data
        type_a_projects = data[self.type_a.id]["projects"]
        self.assertEqual(len(type_a_projects), 2)
        # validate type B data
        type_b_projects = data[self.type_b.id]["projects"]
        self.assertEqual(len(type_b_projects), 3)
        # validate type C data
        type_c_projects = data[self.type_c.id]["projects"]
        self.assertEqual(len(type_c_projects), 2)

        # subscribe to project_a_4 (follow)
        self.project_a_4.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        data = types._get_dashboard_data()
        # validate updated type A data
        type_a_projects = data[self.type_a.id]["projects"]
        self.assertEqual(len(type_a_projects), 3)

        # mark project_a_3 as favorite (star)
        self.project_a_3.write({"is_favorite": True})
        # validate updated type A data
        data = types._get_dashboard_data()
        type_a_projects = data[self.type_a.id]["projects"]
        self.assertEqual(len(type_a_projects), 4)

        # create a new project with dashboard sequence > 0 (but without tasks)
        self.assertEqual(self.type_a.todo_project_count, 5)
        _new_project = self.env["project.project"].create(
            {
                "name": "New project",
                "type_id": self.type_a.id,
                "dashboard_sequence": 10,
            }
        )
        self.assertEqual(self.type_a.todo_project_count, 5)
        # validate updated type A data
        data = types._get_dashboard_data()
        type_a_projects = data[self.type_a.id]["projects"]
        self.assertEqual(len(type_a_projects), 5)
        # add a task to the new project
        _new_task = self.env["project.task"].create(
            {
                "name": "New task",
                "project_id": _new_project.id,
            }
        )
        self.assertEqual(self.type_a.todo_project_count, 6)
        # validate type A same data
        data = types._get_dashboard_data()
        type_a_projects = data[self.type_a.id]["projects"]
        self.assertEqual(len(type_a_projects), 5)

    def test_03_action_open_project(self):
        # test action for 1st project of type A
        action = self.type_a.with_context(
            project_id=self.project_a_0.id
        ).action_open_project()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["view_type"], "form")
        self.assertEqual(action["view_mode"], "form,list")
        self.assertEqual(action["res_model"], "project.project")
        self.assertEqual(action["target"], "current")
        self.assertEqual(action["context"], {"project_id": self.project_a_0.id})
        self.assertEqual(action["res_id"], self.project_a_0.id)

    def test_04_action_open_project_tasks(self):
        # test action for 1st project of type A
        action = self.type_a.with_context(
            project_id=self.project_a_0.id
        ).action_open_project_tasks()
        self.assertEqual(action["name"], "Tasks")
        self.assertEqual(action["res_model"], "project.task")
        # use `safe_eval` to replace `active_id` with its value in the domain
        domain = safe_eval(action.get("domain"), action.get("context"))
        self.assertEqual(
            domain,
            [
                ("project_id", "=", self.project_a_0.id),
                ("display_in_project", "=", True),
            ],
        )

    def test_05_action_open_projects_from_dashboard(self):
        # test action for 1st project of type A
        action = self.type_a.action_open_projects_from_dashboard()
        self.assertEqual(action["name"], "Project")
        self.assertEqual(action["display_name"], "Project")
        self.assertEqual(action["res_model"], "project.project")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(
            action["xml_id"], "project_dashboard.action_project_kanban_from_dashboard"
        )
        self.assertEqual(action["domain"], "[('type_id', 'child_of', active_id)]")
        self.assertEqual(action["context"], "{'default_type_id': active_id}")
        client_context = {"active_id": self.type_a.id}
        # use `safe_eval` to replace `active_id` with its value in the domain
        domain = safe_eval(action.get("domain"), client_context)
        projects = self.env["project.project"].search(domain)
        self.assertEqual(len(projects), 5)  # 5 projects
