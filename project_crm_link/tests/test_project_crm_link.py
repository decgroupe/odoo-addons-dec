# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo.tests.common import TransactionCase


class TestProjectCrmLink(TransactionCase):
    """Test the link between project and crm lead (opportunity)."""

    def assertNameSearchEqual(self, name, projects, expected_results):
        self.env["project.project"].invalidate_model(["display_name"])
        res = self.env["project.project"].name_search(name=name)
        if not expected_results:
            self.assertFalse(res)
            return
        for i, (project, expected_result) in enumerate(
            zip(projects, expected_results, strict=True)
        ):
            self.assertEqual(res[i][0], project.id)
            self.assertEqual(res[i][1], expected_result)

    def setUp(self):
        super().setUp()
        # create projects
        self.project_1 = self.env["project.project"].create({"name": "Test Project 1"})
        self.project_2 = self.env["project.project"].create({"name": "Test Project 2"})
        # create two partners
        self.partner_a = self.env["res.partner"].create({"name": "Test Partner A"})
        self.partner_b = self.env["res.partner"].create({"name": "Test Partner B"})
        # create leads
        self.lead_a = self.env["crm.lead"].create(
            {
                "name": "Test Lead A",
                "partner_id": self.partner_a.id,
                "type": "opportunity",
            }
        )
        self.lead_b = self.env["crm.lead"].create(
            {
                "name": "Test Lead B",
                "partner_id": self.partner_b.id,
                "type": "opportunity",
            }
        )

    def test_01_related_projects(self):
        # test related projects
        self.assertFalse(self.project_1.linked_lead_id)
        self.assertFalse(self.project_2.linked_lead_id)
        self.assertEqual(self.lead_b.related_project_count, 0)
        self.project_1.linked_lead_id = self.lead_a
        self.project_2.linked_lead_id = self.lead_a
        self.assertEqual(self.lead_a.related_project_count, 2)
        self.assertEqual(
            self.lead_a.related_project_ids, self.project_1 | self.project_2
        )
        # change project_2 lead
        self.project_2.linked_lead_id = self.lead_b
        self.assertEqual(self.lead_a.related_project_count, 1)
        self.assertEqual(self.lead_b.related_project_count, 1)
        self.assertEqual(self.lead_a.related_project_ids, self.project_1)
        self.assertEqual(self.lead_b.related_project_ids, self.project_2)
        # delete lead_a and test that project_1 is not deleted but only unlinked
        self.lead_a.unlink()
        self.assertTrue(self.project_1.exists())
        self.assertFalse(self.project_1.linked_lead_id)
        self.assertEqual(self.lead_b.related_project_count, 1)
        self.assertEqual(self.lead_b.related_project_ids, self.project_2)

    def test_02_action_view_related_projects(self):
        # test action view related projects
        action = self.lead_a.action_view_related_projects()
        self.assertEqual(action["domain"], [("linked_lead_id", "in", self.lead_a.ids)])
        self.assertIn("bypass_supermanager_check", action.get("context", {}))
        # add a linked project and test that the default partner is set in the context
        self.assertTrue(self.lead_a.partner_id)
        self.project_1.linked_lead_id = self.lead_a
        action = self.lead_a.action_view_related_projects()
        self.assertEqual(action["domain"], [("linked_lead_id", "in", self.lead_a.ids)])
        self.assertIn("bypass_supermanager_check", action.get("context", {}))
        self.assertEqual(
            action["context"].get("default_partner_id"), self.lead_a.partner_id.id
        )

    def test_03_typefast_and_name_identification(self):
        # test that we can find projects by searching the linked lead name
        self.lead_a.number = "XLD/00080"
        self.lead_b.number = "XLD/00081"
        self.project_1.linked_lead_id = self.lead_a
        self.project_2.linked_lead_id = self.lead_b
        self.assertNameSearchEqual(
            "Lead A", [self.project_1], ["Test Project 1 [XLD/00080] Test Lead A"]
        )
        self.assertNameSearchEqual(
            "Lead B", [self.project_2], ["Test Project 2 [XLD/00081] Test Lead B"]
        )
        # link both projects to the same lead and test that both are found when
        # searching the lead name
        self.project_2.linked_lead_id = self.lead_a
        self.assertNameSearchEqual(
            "Lead A",
            [self.project_1, self.project_2],
            [
                "Test Project 1 [XLD/00080] Test Lead A",
                "Test Project 2 [XLD/00080] Test Lead A",
            ],
        )
