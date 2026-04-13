# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

# simulates the HTML body produced by a mail client when replying:
# the reply text is above the blockquote, the blockquote contains the original
# message with the "reply above this line" marker followed by the quoted content.
REPLY_BODY = """<html>
  <body>
    <p>This is my reply text.</p>
    <blockquote type="cite">
      <div id="reply_above_warning">##- Please type your reply above this line -##</div>
      <p>Original quoted message body goes here.</p>
    </blockquote>
  </body>
</html>"""

# reply whose body contains a forwarded message - the marker is inside the
# forwarded block so the stripping must NOT happen.
FORWARD_BODY = """<html>
  <body>
    <p>Please take a look at this forwarded message.</p>
    <div class="moz-forward-container">
      <br/>
      --- Forwarded Message ---
      <blockquote type="cite">
        <div id="reply_above_warning">
          ##- Please type your reply above this line -##
        </div>
        <p>Forwarded original content.</p>
      </blockquote>
    </div>
  </body>
</html>"""

# reply with an empty body (edge case)
EMPTY_BODY = ""


class TestMailGroupAboveLineCommon(TransactionCase):
    """Common fixtures and helpers for mail_group_above_line tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create an alias domain so the group alias resolves correctly
        cls.alias_domain = cls.env["mail.alias.domain"].create(
            {
                "name": "testcompany.com",
                "bounce_alias": "bounce",
                "catchall_alias": "catchall",
            }
        )
        # create an internal user that will act as message author
        cls.user_author = new_test_user(
            cls.env,
            login="author@testcompany.com",
            groups="base.group_user",
            name="Group Author",
            email="author@testcompany.com",
        )
        # create a public mail group
        cls.test_group = cls.env["mail.group"].create(
            {
                "name": "Test Group",
                "access_mode": "public",
                "alias_name": "test-group",
            }
        )
        # add the author as a member so they can post
        cls.env["mail.group.member"].create(
            {
                "mail_group_id": cls.test_group.id,
                "partner_id": cls.user_author.partner_id.id,
            }
        )
