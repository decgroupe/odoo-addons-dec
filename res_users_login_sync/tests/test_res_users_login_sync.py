# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

import re

from odoo.exceptions import AccessError
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestResUsersLoginSync(TransactionCase):

    def _in_portal(self, user_id):
        return self.env.ref("base.group_portal") in user_id.groups_id

    def _give_portal_access(self, partner_id):
        PortalWizard = self.env["portal.wizard"]
        PortalWizardUser = self.env["portal.wizard.user"]
        wizard_id = PortalWizard.sudo().create({})
        wizard_user_id = PortalWizardUser.sudo().create(
            {
                "wizard_id": wizard_id.id,
                "partner_id": partner_id.id,
                "email": partner_id.email,
                "in_portal": True,
            }
        )
        return wizard_id.action_apply()

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="common-user",
            groups="base.group_user",
            context=ctx,
        )

    def test_01_archive_change_missing_rights(self):
        # Azure Interior, Brandon Freeman
        partner_id = self.env.ref("base.res_partner_address_15")
        self._give_portal_access(partner_id)
        with self.assertRaisesRegex(AccessError, r"You are not allowed to modify"):
            partner_id.with_user(self.user).action_archive()

    def test_02_archive_change_from_partner(self):
        # Azure Interior, Brandon Freeman
        partner_id = self.env.ref("base.res_partner_address_15")
        self._give_portal_access(partner_id)
        partner_user_id = partner_id.user_ids
        self.user.groups_id += self.env.ref("base.group_partner_manager")
        # action archive from partner
        partner_id.with_user(self.user).action_archive()
        self.assertFalse(partner_id.active)
        self.assertFalse(partner_user_id.active)
        # action unarchive from partner
        partner_id.with_user(self.user).action_unarchive()
        self.assertTrue(partner_id.active)
        self.assertTrue(partner_user_id.active)

    def test_03_archive_change_from_user(self):
        # Azure Interior, Brandon Freeman
        partner_id = self.env.ref("base.res_partner_address_15")
        self._give_portal_access(partner_id)
        partner_user_id = partner_id.user_ids
        self.user.groups_id += self.env.ref("base.group_partner_manager")
        # action archive from partner
        partner_id.with_user(self.user).action_archive()
        # partner_user_id.with_user(self.user).action_archive()
        self.assertFalse(partner_id.active)
        self.assertFalse(partner_user_id.active)
        # action unarchive from user (give "Administration/Access Rights")
        self.user.groups_id += self.env.ref("base.group_erp_manager")
        partner_user_id.with_user(self.user).action_unarchive()
        self.assertTrue(partner_user_id.active)
        self.assertTrue(partner_id.active)

    def test_04_try_archive_partner_from_internal_user(self):
        # YourCompany, Marc Demo
        partner_id = self.env.ref("base.partner_demo")
        partner_user_id = partner_id.user_ids
        self.user.groups_id += self.env.ref("base.group_partner_manager")
        # try action archive from partner
        with self.assertRaisesRegex(
            AccessError,
            r"Only administrators are allowed to archive/unarchive internal users "
            "from their partner!",
        ):
            partner_id.with_user(self.user).action_archive()

    def test_05_try_unarchive_partner_from_internal_user(self):
        # YourCompany, Marc Demo
        partner_id = self.env.ref("base.partner_demo")
        partner_user_id = partner_id.user_ids
        partner_id.action_archive()
        self.user.groups_id += self.env.ref("base.group_partner_manager")
        # try action unarchive from partner
        with self.assertRaisesRegex(
            AccessError,
            r"Only administrators are allowed to archive/unarchive internal users "
            "from their partner!",
        ):
            partner_id.with_user(self.user).action_unarchive()

