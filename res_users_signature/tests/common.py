# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestUsersSignatureCommon(TransactionCase):
    """Common fixtures for res_users_signature tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a department with brand overrides
        cls.department = cls.env["hr.department"].create(
            {
                "name": "Test Department",
                "signature_logo_url": "https://example.com/dept-logo.png",
                "signature_color_suffix": "-dept",
                "signature_primary_color": "#123456",
            }
        )
        # create a user with an employee linked to the department
        cls.partner = cls.env["res.partner"].create({"name": "John Doe"})
        cls.user = cls.env["res.users"].create(
            {
                "name": "John Doe",
                "login": "john.doe@example.com",
                "email": "john.doe@example.com",
                "partner_id": cls.partner.id,
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "John Doe",
                "user_id": cls.user.id,
                "work_email": "john.doe@example.com",
                "mobile_phone": "06 12 34 56 78",
                "job_title": "Developer",
                "department_id": cls.department.id,
            }
        )
        # fetch the global template created by module data
        cls.global_template = cls.env.ref("res_users_signature.user_signature_template")
