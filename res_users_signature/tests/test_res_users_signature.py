# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging

from lxml import etree

from odoo.exceptions import UserError

from .common import TestUsersSignatureCommon

_test_logger = logging.getLogger("odoo.tests")


class TestUsersSignature(TestUsersSignatureCommon):
    """Tests for res_users_signature module."""

    # -------------------------------------------------------------------------
    # Template rendering
    # -------------------------------------------------------------------------

    def test_01_render_template_text(self):
        """Render the text body of the global template for a valid user."""
        result = self.global_template._render_template(
            self.global_template.body_text, self.user.id
        )
        self.assertIsNotNone(result)
        self.assertIn("John", result)
        self.assertIn("Doe", result)

    def test_02_render_template_no_employee_raises(self):
        """_render_template raises UserError when user has no linked employee."""
        user_no_emp = self.env["res.users"].create(
            {
                "name": "No Employee",
                "login": "no.employee@example.com",
                "email": "no.employee@example.com",
            }
        )
        with self.assertRaises(UserError):
            self.global_template._render_template(
                self.global_template.body_text, user_no_emp.id
            )

    def test_03_render_template_load_failure_returns_false(self):
        """_render_template returns False when the template text is invalid."""
        result = self.global_template._render_template(None, self.user.id)
        self.assertFalse(result)

    def test_04_build_template_variables(self):
        """_build_template_variables exposes expected keys."""
        variables = self.global_template._build_template_variables(
            self.user, self.employee
        )
        for key in (
            "user",
            "employee",
            "firstname",
            "lastname",
            "email",
            "phone",
            "job_title",
            "website",
            "zip",
        ):
            self.assertIn(key, variables)
        self.assertEqual(variables["firstname"], "John")
        self.assertEqual(variables["lastname"], "Doe")

    def test_05_apply_brand_replacements_logo(self):
        """_apply_brand_replacements replaces logo URL from department settings."""
        # template has logo_url set to /logo.png
        template = self.global_template
        fake_html = f'<img src="{template.logo_url}">'
        result = template._apply_brand_replacements(fake_html, self.employee)
        self.assertNotIn(template.logo_url, result)
        self.assertIn(self.department.signature_logo_url, result)

    def test_06_apply_brand_replacements_color(self):
        """_apply_brand_replacements replaces primary color from department settings."""
        template = self.global_template
        fake_html = f"color: {template.primary_color};"
        result = template._apply_brand_replacements(fake_html, self.employee)
        self.assertNotIn(template.primary_color, result)
        self.assertIn(self.department.signature_primary_color, result)

    # -------------------------------------------------------------------------
    # generate_from_template on res.users
    # -------------------------------------------------------------------------

    def test_07_generate_from_template(self):
        """action_generate_signatures populates the signature fields on the user."""
        self.user.action_generate_signatures()
        self.assertTrue(self.user.signature)

    def test_08_onchange_signature_template_clears_on_none(self):
        """onchange does not error when no template is set."""
        # ensure no template is set, should not raise
        self.user.signature_template = False
        self.user.onchange_signature_template()

    def test_09_onchange_signature_template_generates(self):
        """onchange generates signatures when a template is assigned."""
        self.user.signature_template = self.global_template
        self.user.onchange_signature_template()
        self.assertTrue(self.user.signature)

    # -------------------------------------------------------------------------
    # Signature logo filename
    # -------------------------------------------------------------------------

    def test_10_get_signature_logo_filename_no_ext(self):
        """_get_signature_logo_filename returns the user id when no filename given."""
        fname = self.user._get_signature_logo_filename()
        self.assertEqual(fname, str(self.user.id))

    def test_11_get_signature_logo_filename_with_ext(self):
        """_get_signature_logo_filename appends extension from provided filename."""
        fname = self.user._get_signature_logo_filename("logo.PNG")
        self.assertTrue(fname.endswith(".png"))

    # -------------------------------------------------------------------------
    # View field presence
    # -------------------------------------------------------------------------

    def test_12_res_users_preferences_form_view_fields(self):
        """Expected signature fields are present in the user preferences form view."""
        view = self.env.ref("res_users_signature.res_users_preferences_form_view")
        view_info = self.env["res.users"].get_view(view_id=view.id, view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        for field in (
            "signature_template",
            "signature_text",
            "signature_logo",
            "signature_answer",
            "signature_social_buttons",
        ):
            self.assertIn(field, field_names)

    def test_13_res_users_form_view_fields(self):
        """Expected signature fields are present in the user admin form view."""
        view = self.env.ref("res_users_signature.res_users_form_view")
        view_info = self.env["res.users"].get_view(view_id=view.id, view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        for field in (
            "signature_template",
            "signature_text",
            "signature_logo",
            "signature_answer",
            "signature_social_buttons",
        ):
            self.assertIn(field, field_names)

    def test_14_hr_employee_form_view_fields(self):
        """Expected extra fields are present in the employee form view."""
        view = self.env.ref("res_users_signature.employee_form_view")
        view_info = self.env["hr.employee"].get_view(view_id=view.id, view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        for field in (
            "other_websites",
            "other_work_emails",
            "work_phone_extension",
        ):
            self.assertIn(field, field_names)

    def test_15_hr_department_form_view_fields(self):
        """Expected signature brand fields are present in the department form view."""
        view = self.env.ref("res_users_signature.department_form_view")
        view_info = self.env["hr.department"].get_view(
            view_id=view.id, view_type="form"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        for field in (
            "signature_logo_url",
            "signature_color_suffix",
            "signature_primary_color",
        ):
            self.assertIn(field, field_names)

    # -------------------------------------------------------------------------
    # SELF_WRITEABLE_FIELDS extension
    # -------------------------------------------------------------------------

    def test_16_self_writeable_fields_extended(self):
        """Signature fields are included in SELF_WRITEABLE_FIELDS."""
        writeable = self.user.SELF_WRITEABLE_FIELDS
        for field in (
            "signature_text",
            "signature_answer",
            "signature_template",
            "signature_social_buttons",
            "signature_logo",
            "signature_logo_filename",
        ):
            self.assertIn(field, writeable)

    # -------------------------------------------------------------------------
    # Notification signature replacement
    # -------------------------------------------------------------------------

    def test_17_notify_signature_replaced_for_internal_message(self):
        """The shorter answer signature is used for internal mail messages."""
        # set a short answer signature on the user
        self.user.write({"signature_answer": "<p>Short</p>"})
        # create a fake internal message
        subtype_internal = self.env.ref("mail.mt_note")
        message = self.env["mail.message"].create(
            {
                "model": "res.partner",
                "res_id": self.partner.id,
                "author_id": self.user.partner_id.id,
                "subtype_id": subtype_internal.id,
                "email_add_signature": True,
                "body": "<p>Test</p>",
            }
        )
        render_ctx = self.partner._notify_by_email_prepare_rendering_context(
            message,
            msg_vals={"author_id": self.user.partner_id.id},
        )
        self.assertEqual(render_ctx["signature"], "<p>Short</p>")
