# Copyright 2021 DEC SARL, Inc - All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from .common import TestMailActivityRedirectionCommon


class TestMailActivityRedirection(TestMailActivityRedirectionCommon):
    """Tests for the mail_activity_redirection module."""

    def _make_rule(self, **kwargs):
        """Create a redirection rule with the given kwargs and return it."""
        vals = {
            "name": "Test Redirection Rule",
            "user_id": self.user_target.id,
        }
        vals.update(kwargs)
        return self.Redirection.create(vals)

    def test_01_match_no_filters(self):
        """A rule with no filters matches any activity parameters."""
        rule = self._make_rule(regex_pattern=".*")
        self.assertTrue(
            rule.match(
                model_name="res.partner",
                type_xmlid="mail.mail_activity_data_todo",
                type_id=self.activity_type.id,
                user_id=self.user_original.id,
                qweb_template_xmlid=None,
                note="some note",
            )
        )

    def test_02_match_by_initial_user_match(self):
        """A rule with initial_user_ids matches when user_id is in the list."""
        rule = self._make_rule(
            initial_user_ids=self.user_original.ids,
            regex_pattern=".*",
        )
        self.assertTrue(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=self.user_original.id,
                qweb_template_xmlid=None,
                note="note",
            )
        )

    def test_03_match_by_initial_user_no_match(self):
        """A rule with initial_user_ids does not match when user_id is not in the
        list."""
        rule = self._make_rule(
            initial_user_ids=self.user_original.ids,
            regex_pattern=".*",
        )
        other_user = self.env.ref("base.user_admin")
        self.assertFalse(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=other_user.id,
                qweb_template_xmlid=None,
                note="note",
            )
        )

    def test_04_match_by_model_match(self):
        """A rule with model_ids matches when model_name is in the list."""
        rule = self._make_rule(
            model_ids=self.partner_model.ids,
            regex_pattern=".*",
        )
        self.assertTrue(
            rule.match(
                model_name="res.partner",
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="note",
            )
        )

    def test_05_match_by_model_no_match(self):
        """A rule with model_ids does not match when model_name is not in the list."""
        rule = self._make_rule(
            model_ids=self.partner_model.ids,
            regex_pattern=".*",
        )
        self.assertFalse(
            rule.match(
                model_name="res.users",
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="note",
            )
        )

    def test_06_match_by_activity_type_xmlid(self):
        """A rule with activity_type_ids matches when type_xmlid refers to one of
        them."""
        rule = self._make_rule(
            activity_type_ids=self.activity_type.ids,
            regex_pattern=".*",
        )
        # match by xmlid
        self.assertTrue(
            rule.match(
                model_name=None,
                type_xmlid="mail.mail_activity_data_todo",
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="note",
            )
        )
        # no match by xmlid
        self.assertFalse(
            rule.match(
                model_name=None,
                type_xmlid="mail.mail_activity_data_email",
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="note",
            )
        )

    def test_07_match_by_activity_type_id(self):
        """A rule with activity_type_ids matches when type_id is in the list."""
        rule = self._make_rule(
            activity_type_ids=self.activity_type.ids,
            regex_pattern=".*",
        )
        # match by id
        self.assertTrue(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=self.activity_type.id,
                user_id=None,
                qweb_template_xmlid=None,
                note="note",
            )
        )
        # no match: neither xmlid nor type_id
        self.assertFalse(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="note",
            )
        )

    def test_08_match_by_regex_match(self):
        """A rule with a regex_pattern matches when the note matches the pattern."""
        rule = self._make_rule(regex_pattern=r"urgent")
        self.assertTrue(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="this is urgent: please act",
            )
        )

    def test_09_match_by_regex_no_match(self):
        """A rule with a regex_pattern does not match when the note does not match."""
        rule = self._make_rule(regex_pattern=r"urgent")
        self.assertFalse(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="nothing special here",
            )
        )

    def test_10_match_bytes_note(self):
        """The match method handles a bytes note by decoding it first."""
        rule = self._make_rule(regex_pattern=r"urgent")
        self.assertTrue(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note=b"urgent bytes note",
            )
        )

    def test_11_match_empty_note_no_match(self):
        """A rule with a regex_pattern does not match when note is empty."""
        rule = self._make_rule(regex_pattern=r"urgent")
        self.assertFalse(
            rule.match(
                model_name=None,
                type_xmlid=None,
                type_id=None,
                user_id=None,
                qweb_template_xmlid=None,
                note="",
            )
        )

    def test_12_activity_schedule_redirect(self):
        """activity_schedule redirects the activity user when a rule matches."""
        rule = self._make_rule(regex_pattern=".*")
        activity = self.partner.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_todo",
            note="some work to do",
            user_id=self.user_original.id,
        )
        # the activity must have been redirected to user_target
        self.assertEqual(activity.user_id, self.user_target)
        # the activity must be linked in the rule history
        self.assertIn(activity, rule.activity_ids)

    def test_13_activity_schedule_no_match_not_redirected(self):
        """activity_schedule does not redirect when no rule matches."""
        # rule only matches a specific user (different from user_original)
        other_user = self.env.ref("base.user_admin")
        self._make_rule(
            initial_user_ids=other_user.ids,
            regex_pattern=".*",
        )
        activity = self.partner.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_todo",
            note="some work to do",
            user_id=self.user_original.id,
        )
        # the activity must stay assigned to user_original
        self.assertEqual(activity.user_id, self.user_original)

    def test_14_link_to_redirection_max_five(self):
        """_link_to_mail_activity_redirection keeps at most 5 activities."""
        rule = self._make_rule(regex_pattern=".*")
        # schedule 7 activities
        activities = self.env["mail.activity"]
        for _ in range(7):
            act = self.partner.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                note="work to do",
                user_id=self.user_original.id,
            )
            activities |= act
        # the rule should only keep the last 5 activities
        self.assertEqual(len(rule.activity_ids), 5)

    def test_15_default_sequence_increments(self):
        """_default_sequence returns a value higher than the last existing rule."""
        rule1 = self._make_rule(name="Rule A", sequence=10)
        rule2 = self.Redirection.new({})
        self.assertGreater(rule2.sequence, rule1.sequence)

    def test_16_form_view_fields(self):
        """Expected fields are present in the combined form view arch."""
        view_info = self.env["mail.activity.redirection"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("user_id", field_names)
        self.assertIn("initial_user_ids", field_names)
        self.assertIn("model_ids", field_names)
        self.assertIn("activity_type_ids", field_names)
        self.assertIn("regex_pattern", field_names)
        self.assertIn("activity_ids", field_names)

    def test_17_list_view_fields(self):
        """Expected fields are present in the combined list view arch."""
        view_info = self.env["mail.activity.redirection"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("user_id", field_names)
        self.assertIn("model_ids", field_names)
        self.assertIn("regex_pattern", field_names)
