# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import MailActivityTeamImageCommon


class TestMailActivityTeamImage(MailActivityTeamImageCommon):
    """Tests for mail_activity_team_image module."""

    def test_01_team_has_image_fields(self):
        """Verify that mail.activity.team exposes image mixin fields."""
        team = self.team
        self.assertIn("image_1920", self.env["mail.activity.team"]._fields)
        self.assertIn("image_128", self.env["mail.activity.team"]._fields)
        self.assertFalse(team.image_1920)

    def test_02_team_image_can_be_set(self):
        """Verify that an image can be written and read back on a team."""
        # 1x1 transparent PNG encoded in base64
        png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
            "YPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        self.team.image_1920 = png_b64
        self.env.invalidate_all()
        self.assertTrue(self.team.image_128)

    def test_03_form_view_contains_image_field(self):
        """Check that image_1920 is present in the combined team form view arch."""
        view_info = self.env["mail.activity.team"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("image_1920", field_names)
