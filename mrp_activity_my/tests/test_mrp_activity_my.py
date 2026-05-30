# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestMrpActivityMyCommon


class TestMrpActivityMy(TestMrpActivityMyCommon):
    """Tests for mrp_activity_my views."""

    def test_01_list_view_contains_activity_widget(self):
        """Verify the inherited list view contains the activity_my widget field."""
        view = self.env.ref("mrp_activity_my.mrp_production_tree_view")
        view_info = self.env["mrp.production"].get_view(
            view_id=view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"])
        field_nodes = arch.xpath("//field[@name='activity_my_ids']")
        self.assertTrue(field_nodes)
        self.assertEqual(field_nodes[0].get("widget"), "list_activity_my")

    def test_02_kanban_view_contains_activity_fields(self):
        """Verify kanban view exposes activity_my fields
        and progressbar."""
        view = self.env.ref("mrp_activity_my.mrp_production_kanban_view")
        view_info = self.env["mrp.production"].get_view(
            view_id=view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"])
        self.assertTrue(arch.xpath("//field[@name='activity_my_ids']"))
        self.assertTrue(arch.xpath("//field[@name='activity_my_state']"))
        self.assertTrue(arch.xpath("//progressbar[@field='activity_my_state']"))

    def test_03_staged_kanban_view_contains_activity_fields(self):
        """Verify staged kanban view also exposes activity_my fields."""
        view = self.env.ref("mrp_activity_my.mrp_production_staged_kanban_view")
        view_info = self.env["mrp.production"].get_view(
            view_id=view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"])
        self.assertTrue(arch.xpath("//field[@name='activity_my_ids']"))
        self.assertTrue(arch.xpath("//field[@name='activity_my_state']"))
        self.assertTrue(arch.xpath("//progressbar[@field='activity_my_state']"))
