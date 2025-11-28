# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2025


from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestCreateItems(TransactionCase):
    def setUp(self):
        super().setUp()

    def _create_wizard(self, content):
        wizard = self.env["create.items.wizard"].create({"content": content})
        return wizard

    def test_01_wizard_create_activities(self):
        """Test wizard creates activities correctly"""
        wizard = self._create_wizard(
            """
            <ul>
                <li>Reading Comprehension</li>
                <li>Writing Exercise</li>
                <li>Listening Practice</li>
            </ul>
            """
        )

        # Check preview
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].name, "Reading Comprehension")
        self.assertEqual(wizard.line_ids[1].name, "Writing Exercise")
        self.assertEqual(wizard.line_ids[2].name, "Listening Practice")

    def test_02_wizard_create_activities_from_table(self):
        """Test wizard creates activities with codes from table"""
        wizard = self._create_wizard(
            """
            <table>
                <tr>
                    <td>A1</td>
                    <td>Reading Comprehension</td>
                </tr>
                <tr>
                    <td>A2</td>
                    <td>Writing Exercise</td>
                </tr>
                <tr>
                    <td>A3</td>
                    <td>Listening Practice</td>
                </tr>
            </table>
            """,
        )

        # Check preview
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].identifier, "A1")
        self.assertEqual(wizard.line_ids[0].name, "Reading Comprehension")
        self.assertEqual(wizard.line_ids[1].identifier, "A2")
        self.assertEqual(wizard.line_ids[1].name, "Writing Exercise")
        self.assertEqual(wizard.line_ids[2].identifier, "A3")
        self.assertEqual(wizard.line_ids[2].name, "Listening Practice")

    def test_03_wizard_create_activities_from_table_single_column(self):
        """Test wizard creates activities from single column table"""
        wizard = self._create_wizard(
            """
            <table>
                <tr>
                    <td>Reading Comprehension</td>
                </tr>
                <tr>
                    <td>Writing Exercise</td>
                </tr>
            </table>
            """,
        )

        # Check preview
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(wizard.line_ids[0].identifier, "")
        self.assertEqual(wizard.line_ids[0].name, "Reading Comprehension")
        self.assertEqual(wizard.line_ids[1].identifier, "")
        self.assertEqual(wizard.line_ids[1].name, "Writing Exercise")

    def test_04_wizard_create_activities_from_table_empty_code(self):
        """Test wizard creates activities from table with empty codes"""
        wizard = self._create_wizard(
            """
            <table>
                <tr>
                    <td></td>
                    <td>Reading Comprehension</td>
                </tr>
                <tr>
                    <td>A2</td>
                    <td>Writing Exercise</td>
                </tr>
            </table>
            """,
        )

        # Check preview
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(wizard.line_ids[0].identifier, "")
        self.assertEqual(wizard.line_ids[0].name, "Reading Comprehension")
        self.assertEqual(wizard.line_ids[1].identifier, "A2")
        self.assertEqual(wizard.line_ids[1].name, "Writing Exercise")

    def test_05_wizard_empty_content_error(self):
        """Test wizard raises error with empty content"""
        wizard = self._create_wizard("")
        with self.assertRaises(UserError):
            wizard.action_create_items()

    def test_06_wizard_no_parseable_content_error(self):
        """Test wizard raises error when content cannot be parsed"""
        wizard = self.env["create.items.wizard"].create({"content": "<div></div>"})
        with self.assertRaises(UserError):
            wizard.action_create_items()

    def test_07_wizard_onchange_content(self):
        """Test onchange content triggers parsing"""
        wizard = self.env["create.items.wizard"].create({})
        wizard.content = """
        <ul>
            <li>Item A</li>
            <li>Item B</li>
        </ul>
        """
        wizard._onchange_content()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(wizard.line_ids[0].name, "Item A")
        self.assertEqual(wizard.line_ids[1].name, "Item B")

    def test_08_wizard_onchange_separator(self):
        """Test onchange separator re-parses content"""
        wizard = self._create_wizard(
            """
            <ul>
                <li>A1=>Item One</li>
                <li>A2=>Item Two</li>
            </ul>
            """
        )
        wizard.action_parse_content()
        # Initially, no separator detected (=> not in default list)
        self.assertEqual(len(wizard.line_ids), 2)

        # Now set custom separator
        wizard.content_separator = "=>"
        wizard._onchange_content_separator()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(wizard.line_ids[0].identifier, "A1")
        self.assertEqual(wizard.line_ids[0].name, "Item One")

    def test_09_wizard_action_parse_empty_content(self):
        """Test parsing clears lines when content is empty"""
        wizard = self._create_wizard(
            """
            <ul>
                <li>Item A</li>
            </ul>
            """
        )
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 1)

        # Clear content
        wizard.content = ""
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 0)

    def test_10_wizard_reopen_action(self):
        """Test _reopen returns correct action"""
        wizard = self._create_wizard("<ul><li>Test</li></ul>")
        action = wizard._reopen()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "create.items.wizard")
        self.assertEqual(action["res_id"], wizard.id)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")

    def test_11_wizard_action_create_items_default(self):
        """Test action_create_items default behavior"""
        wizard = self._create_wizard(
            """
            <ul>
                <li>Item One</li>
                <li>Item Two</li>
            </ul>
            """
        )
        # Should call action_parse_content if content exists
        action = wizard.action_create_items()
        self.assertEqual(len(wizard.line_ids), 2)
        self.assertEqual(action["type"], "ir.actions.act_window")

    def test_12_wizard_line_required_fields(self):
        """Test wizard line model required fields"""
        wizard = self._create_wizard("<ul><li>Test</li></ul>")
        wizard.action_parse_content()
        line = wizard.line_ids[0]
        self.assertTrue(line.wizard_id)
        self.assertTrue(line.name)

    def test_13_wizard_with_plaintext_dash_list(self):
        """Test wizard with plaintext dash list"""
        wizard = self._create_wizard(
            """
            - Item One
            - Item Two
            - Item Three
            """
        )
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].name, "Item One")

    def test_14_wizard_with_separator_detection(self):
        """Test wizard detects and uses separator"""
        wizard = self._create_wizard(
            """
            <ul>
                <li>CODE1: First Item</li>
                <li>CODE2: Second Item</li>
                <li>CODE3: Third Item</li>
            </ul>
            """
        )
        wizard.action_parse_content()
        self.assertEqual(wizard.content_separator, ":")
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].identifier, "CODE1")
        self.assertEqual(wizard.line_ids[0].name, "First Item")

    def test_15_wizard_ordered_list(self):
        """Test wizard with ordered list"""
        wizard = self._create_wizard(
            """
            <ol>
                <li>First</li>
                <li>Second</li>
                <li>Third</li>
            </ol>
            """
        )
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 3)
        self.assertEqual(wizard.line_ids[0].name, "First")
        self.assertEqual(wizard.line_ids[1].name, "Second")

    def test_16_wizard_empty_content(self):
        """Test wizard handles empty content gracefully"""
        wizard = self._create_wizard("   ")
        wizard.action_parse_content()
        self.assertEqual(len(wizard.line_ids), 0)
        self.assertFalse(wizard.content_separator)
