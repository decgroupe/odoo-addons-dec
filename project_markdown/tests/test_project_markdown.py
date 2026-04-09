# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from odoo.tests import Form

from .common import TestProjectMarkdownCommon


class TestProjectMarkdown(TestProjectMarkdownCommon):
    """Tests for project_markdown module."""

    def test_01_field_defaults(self):
        """Check default values for description visibility fields."""
        self.assertTrue(self.task.description_html_visible)
        self.assertFalse(self.task.description_markdown_visible)

    def test_02_description_fields_exist(self):
        """Check that markdown and html description fields are set/get correctly."""
        self.task.description = "<p>HTML content</p>"
        self.task.description_markdown = "# Markdown content"
        self.task.invalidate_recordset()
        self.assertIn("HTML content", self.task.description)
        self.assertEqual(self.task.description_markdown, "# Markdown content")

    def test_03_form_view_fields(self):
        """Check that expected fields are present in the combined form view arch."""
        view_info = self.env["project.task"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("description_markdown", field_names)
        self.assertIn("description_html_visible", field_names)
        self.assertIn("description_markdown_visible", field_names)

    def test_04_description_html_invisible_when_flag_false(self):
        """description field is invisible in form view when
        description_html_visible is False."""
        self.task.description_html_visible = False
        with Form(self.task, view="project_markdown.project_task_form") as form:
            self.assertTrue(form._get_modifier("description", "invisible"))

    def test_05_description_html_visible_when_flag_true(self):
        """description field is visible in form view when
        description_html_visible is True."""
        self.task.description_html_visible = True
        with Form(self.task, view="project_markdown.project_task_form") as form:
            self.assertFalse(form._get_modifier("description", "invisible"))

    def test_06_description_markdown_invisible_when_flag_false(self):
        """description_markdown field is invisible when
        description_markdown_visible is False."""
        self.task.description_markdown_visible = False
        with Form(self.task, view="project_markdown.project_task_form") as form:
            self.assertTrue(form._get_modifier("description_markdown", "invisible"))

    def test_07_description_markdown_visible_when_flag_true(self):
        """description_markdown field is visible when
        description_markdown_visible is True."""
        self.task.description_markdown_visible = True
        with Form(self.task, view="project_markdown.project_task_form") as form:
            self.assertFalse(form._get_modifier("description_markdown", "invisible"))
