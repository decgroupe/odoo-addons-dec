# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from .common import (
    FORWARD_BODY,
    REPLY_BODY,
    TestMailGroupAboveLineCommon,
)


class TestMailGroupAboveLine(TestMailGroupAboveLineCommon):
    """Tests for mail_group_above_line module."""

    def _post_message(self, body):
        """Call message_post on the test group and return the resulting mail.message."""
        msg = self.test_group.message_post(
            body=body,
            subject="Test Subject",
            email_from=self.user_author.email_formatted,
            message_type="email",
        )
        return msg

    def test_01_reply_above_line_strips_quoted_content(self):
        """Check that content below the reply marker is removed from the stored body."""
        msg = self._post_message(REPLY_BODY)
        self.assertNotIn(
            "##- Please type your reply above this line -##",
            msg.body,
        )
        self.assertIn("##- Content Removed -##", msg.body)
        # the actual reply text above the marker must be kept
        self.assertIn("This is my reply text.", msg.body)

    def test_02_forwarded_message_is_not_stripped(self):
        """Check that forwarded messages are left untouched."""
        msg = self._post_message(FORWARD_BODY)
        # the marker is inside a forwarded block - content must NOT be replaced
        self.assertIn(
            "##- Please type your reply above this line -##",
            msg.body,
        )
        self.assertNotIn("##- Content Removed -##", msg.body)
        # the forwarded content must still be present
        self.assertIn("Forwarded original content.", msg.body)

    def test_03_whitespace_body_is_left_unchanged(self):
        """Check that a whitespace-only body is left unchanged."""
        msg = self._post_message("<p> </p>")
        self.assertNotIn("##- Content Removed -##", msg.body)

    def test_04_body_without_marker_is_left_unchanged(self):
        """Check that a plain reply without the marker is stored verbatim."""
        plain_body = "<p>Just a normal message with no marker.</p>"
        msg = self._post_message(plain_body)
        self.assertNotIn("##- Content Removed -##", msg.body)
        self.assertIn("Just a normal message with no marker.", msg.body)
