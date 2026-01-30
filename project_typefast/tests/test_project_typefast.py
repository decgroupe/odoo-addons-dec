# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestProjectTypefast(TransactionCase):
    """Test Project Typefast Module"""

    def test_01_project_name(self):
        project = self.env["project.project"].create({"name": "⌛ Project Typefast"})
        self.assertEqual(project.typefast_name, "ProjectTypefast")
