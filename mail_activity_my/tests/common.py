# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from datetime import timedelta

from odoo_test_helper import FakeModelLoader

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestMailActivityMyCommon(TransactionCase):
    """Base class for mail_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.addClassCleanup(cls.loader.restore_registry)
        cls.loader.backup_registry()
        # pylint: disable=import-outside-toplevel
        from .models import MailActivityMyTestModel

        cls.loader.update_registry((MailActivityMyTestModel,))
        # register fake model in attrs_before so check_attrs does not flag
        # the mixin fields as unexpected after each test
        fake_model_cls = cls.env.registry["mail.activity.my.test.model"]
        cls.attrs_before["mail.activity.my.test.model"] = set(vars(fake_model_cls)) | {
            "__annotations__",
            "__annotate_func__",
            "__annotations_cache__",
        }
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.TestModel = cls.env["mail.activity.my.test.model"]
        cls.ActivityModel = cls.env["mail.activity"]
        cls.test_model_id = cls.env["ir.model"]._get("mail.activity.my.test.model")
        cls.activity_type = cls.env["mail.activity.type"].create(
            {"name": "Test My Activity Type"}
        )
        # use superuser (uid=1) so domain ("user_id", "=", self._uid) matches
        cls.user = cls.env.ref("base.user_root")
        cls.user2 = cls.env["res.users"].create(
            {
                "name": "Test User 2",
                "login": "test_user_2_mail_act_my",
                "email": "test2_mail_act_my@test.com",
                "groups_id": [Command.set([cls.env.ref("base.group_user").id])],
            }
        )
        cls.record = cls.TestModel.create({"name": "Test Record"})

    def _make_activity(self, record, user, days_from_today=0):
        """Create a test activity for the given record and user."""
        deadline = fields.Date.today() + timedelta(days=days_from_today)
        return self.ActivityModel.sudo().create(
            {
                "activity_type_id": self.activity_type.id,
                "res_id": record.id,
                "res_model_id": self.test_model_id.id,
                "user_id": user.id,
                "date_deadline": deadline,
            }
        )
