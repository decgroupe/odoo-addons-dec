# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.exceptions import UserError
from odoo.fields import Command

from .common import TestBaseMergeCommon


class TestBaseMerge(TestBaseMergeCommon):
    """Tests for generic merge.object.wizard behavior."""

    def test_01_merge_updates_relations_and_sums_values(self):
        """Merge records and ensure relational/reference links are redirected."""
        dst = self.merge_model.create({"name": "Destination", "amount": 2})
        src = self.merge_model.create({"name": "Source", "amount": 3})
        holder = self.holder_model.create(
            {
                "name": "Holder",
                "merge_id": src.id,
                "ref": f"{src._name},{src.id}",
            }
        )
        wizard = self.wizard_model.create(
            {
                "object_ids": (dst + src).ids,
                "dst_object_id": dst.id,
            }
        )
        wizard.action_merge()
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        self.assertEqual(dst.amount, 5)
        self.assertEqual(holder.merge_id.id, dst.id)
        self.assertEqual(holder.ref, dst)

    def test_02_merge_respects_max_objects_parameter(self):
        """Block merge when selected records exceed configured maximum."""
        records = self.merge_model.create(
            [
                {"name": "R1"},
                {"name": "R2"},
                {"name": "R3"},
                {"name": "R4"},
            ]
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "base_merge.merge_objects_max_number", "3"
        )
        wizard = self.wizard_model.create(
            {
                "object_ids": records.ids,
                "dst_object_id": records[0].id,
            }
        )
        with self.assertRaisesRegex(UserError, "For safety reasons"):
            wizard.action_merge()

    def test_03_merge_rejects_parent_child_selection(self):
        """Prevent merge when source set includes parent and child records."""
        parent = self.merge_model.create({"name": "Parent"})
        child = self.merge_model.create({"name": "Child", "parent_id": parent.id})
        wizard = self.wizard_model.create(
            {
                "object_ids": (parent + child).ids,
                "dst_object_id": parent.id,
            }
        )
        with self.assertRaisesRegex(UserError, "one of his parent"):
            wizard.action_merge()

    def test_04_merge_unique_xmlid_keeps_single_identifier(self):
        """Keep exactly one XML-ID on destination when unique_xmlid is requested."""
        dst = self.merge_model.create({"name": "Destination"})
        src = self.merge_model.create({"name": "Source"})
        self._create_xmlid(dst, "test_dst_xmlid")
        self._create_xmlid(src, "test_src_xmlid")
        wizard = self.wizard_model.create(
            {
                "object_ids": (dst + src).ids,
                "dst_object_id": dst.id,
            }
        )
        wizard._merge((dst + src).ids, dst_object=dst, unique_xmlid=True)
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        xmlids = (
            self.env["ir.model.data"]
            .sudo()
            .search([("model", "=", dst._name), ("res_id", "=", dst.id)])
        )
        self.assertEqual(len(xmlids), 1)

    def test_05_default_get_and_action_helpers(self):
        """Cover default_get path and helper actions for wizard navigation."""
        first = self.merge_model.create({"name": "First"})
        second = self.merge_model.create({"name": "Second"})
        defaults = self.wizard_model.with_context(
            active_model=self.merge_model._name,
            active_ids=(first + second).ids,
        ).default_get(["state", "object_ids", "dst_object_id"])
        self.assertEqual(defaults["state"], "selection")
        self.assertEqual(set(defaults["object_ids"][0][2]), set((first + second).ids))
        self.assertIn(defaults["dst_object_id"], (first + second).ids)
        wizard = self.wizard_model.create({})
        action = wizard.action_merge()
        self.assertEqual(wizard.state, "finished")
        self.assertEqual(action["res_model"], wizard._name)
        self.assertEqual(action["target"], "new")
        action = wizard.action_skip()
        self.assertEqual(action["res_model"], wizard._name)
        self.assertEqual(action["target"], "new")
        self.assertEqual(wizard.state, "finished")

    def test_06_merge_updates_ir_attachment_references(self):
        """Attachments referencing a source record are re-linked to destination."""
        dst = self.merge_model.create({"name": "Destination"})
        src = self.merge_model.create({"name": "Source"})
        attachment = (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": "Test Attachment",
                    "res_model": src._name,
                    "res_id": src.id,
                }
            )
        )
        wizard = self.wizard_model.create(
            {
                "object_ids": (dst + src).ids,
                "dst_object_id": dst.id,
            }
        )
        wizard.action_merge()
        attachment.invalidate_recordset()
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        self.assertEqual(attachment.res_id, dst.id)

    def test_07_merge_updates_ir_model_data_references(self):
        """XML-IDs referencing a source record are re-linked to destination."""
        dst = self.merge_model.create({"name": "Destination"})
        src = self.merge_model.create({"name": "Source"})
        xmlid = self._create_xmlid(src, "test_ref_xmlid_src")
        wizard = self.wizard_model.create(
            {
                "object_ids": (dst + src).ids,
                "dst_object_id": dst.id,
            }
        )
        wizard.action_merge()
        xmlid.invalidate_recordset()
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        self.assertEqual(xmlid.res_id, dst.id)

    def test_08_merge_advanced_fields(self):
        """After merge, floats are summed, selection kept from dst, m2m tags merged."""
        tag1 = self.tag_model.create({"name": "Tag1"})
        tag2 = self.tag_model.create({"name": "Tag2"})
        dst = self.merge_model.create(
            {
                "name": "Destination",
                "amount": 10,
                "amount_float": 1.5,
                "state": "done",
                "description": "Dst description",
                "tag_ids": [Command.link(tag1.id)],
            }
        )
        src = self.merge_model.create(
            {
                "name": "Source",
                "amount": 5,
                "amount_float": 2.5,
                "state": "draft",
                "description": "Src description",
                "tag_ids": [Command.link(tag2.id)],
            }
        )
        wizard = self.wizard_model.create(
            {
                "object_ids": (dst + src).ids,
                "dst_object_id": dst.id,
            }
        )
        wizard.action_merge()
        dst.invalidate_recordset()
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        self.assertEqual(dst.amount, 15)
        self.assertAlmostEqual(dst.amount_float, 4.0)
        self.assertEqual(dst.state, "done")
        self.assertIn(tag1, dst.tag_ids)
        self.assertIn(tag2, dst.tag_ids)

    def test_09_merge_fewer_than_two_objects_is_noop(self):
        """Calling _merge with a single record silently returns without changes."""
        record = self.merge_model.create({"name": "Solo"})
        wizard = self.wizard_model.create({})
        wizard._merge([record.id])
        self.assertTrue(record.exists())

    def test_10_merge_invalid_max_param_raises_user_error(self):
        """A non-integer merge_objects_max_number param raises a UserError."""
        self.env["ir.config_parameter"].sudo().set_param(
            "base_merge.merge_objects_max_number", "not_a_number"
        )
        r1 = self.merge_model.create({"name": "R1"})
        r2 = self.merge_model.create({"name": "R2"})
        wizard = self.wizard_model.create(
            {"object_ids": (r1 + r2).ids, "dst_object_id": r1.id}
        )
        with self.assertRaisesRegex(UserError, "Invalid system parameter"):
            wizard.action_merge()

    def test_11_merge_auto_selects_destination_when_none_given(self):
        """When no dst_object is passed, _merge picks the oldest record as dst."""
        r1 = self.merge_model.create({"name": "R1"})
        r2 = self.merge_model.create({"name": "R2"})
        wizard = self.wizard_model.create({"object_ids": (r1 + r2).ids})
        wizard._merge([r1.id, r2.id])
        survivors = (r1 + r2).exists()
        self.assertEqual(len(survivors), 1)

    def test_12_merge_propagates_src_parent_id_to_dst(self):
        """When src has a parent_id, it is written to dst
        after a successful merge."""
        grandparent = self.merge_model.create({"name": "Grandparent"})
        dst = self.merge_model.create({"name": "Destination"})
        src = self.merge_model.create({"name": "Source", "parent_id": grandparent.id})
        wizard = self.wizard_model.create(
            {"object_ids": (dst + src).ids, "dst_object_id": dst.id}
        )
        wizard.action_merge()
        dst.invalidate_recordset()
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())
        self.assertEqual(dst.parent_id, grandparent)

    def test_13_unique_xmlid_merge_succeeds_with_src_xmlid_only(self):
        """With unique_xmlid=True and only src holding an xmlid, merge succeeds."""
        dst = self.merge_model.create({"name": "Destination"})
        src = self.merge_model.create({"name": "Source"})
        self._create_xmlid(src, "test_src_only_xmlid_unique")
        wizard = self.wizard_model.create(
            {"object_ids": (dst + src).ids, "dst_object_id": dst.id}
        )
        wizard._merge((dst + src).ids, dst_object=dst, unique_xmlid=True)
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())

    def test_14_object_use_in_returns_false_for_empty_model_map(self):
        """_object_use_in with an empty model map always evaluates to False."""
        wizard = self.wizard_model.create({})
        result = wizard._object_use_in([1, 2, 3], {})
        self.assertFalse(result)

    def test_15_compute_models_returns_empty_mapping(self):
        """_compute_models returns an empty dict by default."""
        wizard = self.wizard_model.create({})
        result = wizard._compute_models()
        self.assertEqual(result, {})

    def test_16_wizard_navigation_with_line_ids(self):
        """action_skip and action_merge navigate wizard lines and unlink them."""
        r1 = self.env["merge.dummy"].create({"name": "Dummy1"})
        r2 = self.env["merge.dummy"].create({"name": "Dummy2"})
        r3 = self.env["merge.dummy"].create({"name": "Dummy3"})
        r4 = self.env["merge.dummy"].create({"name": "Dummy4"})
        base_wizard = self.env["merge.object.wizard"].create(
            {
                "state": "selection",
                "object_ids": (r1 + r2).ids,
                "dst_object_id": r2.id,
            }
        )
        line1 = self.env["merge.object.line"].create(
            {
                "wizard_id": base_wizard.id,
                "aggr_ids": str([r1.id, r2.id]),
                "min_id": r1.id,
            }
        )
        line2 = self.env["merge.object.line"].create(
            {
                "wizard_id": base_wizard.id,
                "aggr_ids": str([r3.id, r4.id]),
                "min_id": r3.id,
            }
        )
        base_wizard.current_line_id = line1.id
        # action_skip unlinks line1 then navigates to line2
        action = base_wizard.action_skip()
        self.assertFalse(line1.exists())
        self.assertEqual(action["res_model"], base_wizard._name)
        self.assertEqual(base_wizard.state, "selection")
        self.assertEqual(base_wizard.current_line_id, line2)
        # action_merge processes r3+r4 and unlinks line2
        action = base_wizard.action_merge()
        self.assertFalse(line2.exists())
        self.assertEqual(action["res_model"], base_wizard._name)
