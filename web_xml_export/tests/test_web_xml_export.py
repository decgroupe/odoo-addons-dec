# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026


from odoo import Command
from odoo.tests import tagged

from odoo.addons.web_xml_export.tests.common import TestWebXmlExportBase


@tagged("post_install", "-at_install")
class TestWebXmlExport(TestWebXmlExportBase):
    """Tests for Web XML Export"""

    def setUp(self):
        super().setUp()

    def test_01_module_export(self):
        model = self.env["ir.module.module"]
        domain = [("name", "in", ["base", "bus", "web"])]
        modules = model.search(domain)
        export = self.export(
            model, fields=["name", "author", "state"], params={"ids": modules.ids}
        )
        self.assertExportEqual(
            export,
            """
            <?xml version="1.0" ?>
            <odoo>
                <record model="ir.module.module" id="base.module_base">
                    <field name="name">base</field>
                    <field name="author">Odoo S.A.</field>
                    <field name="state">installed</field>
                </record>
                <record model="ir.module.module" id="base.module_bus">
                    <field name="name">bus</field>
                    <field name="author">Odoo S.A.</field>
                    <field name="state">installed</field>
                </record>
                <record model="ir.module.module" id="base.module_web">
                    <field name="name">web</field>
                    <field name="author">Odoo S.A.</field>
                    <field name="state">installed</field>
                </record>
            </odoo>
            """,
        )

    def test_02_user_export(self):
        model = self.env["res.users"]
        domain = []
        users = model.search(domain)
        export = self.export(
            model,
            fields=["login", "name", "lang", "login_date"],
            params={"ids": users.ids},
        )
        self.assertExportEqual(
            export,
            """
            <?xml version="1.0" ?>
            <odoo>
                <record model="res.users" id="base.demo_user0">
                    <field name="login">portal</field>
                    <field name="name">Joel Willis</field>
                    <field name="lang">en_US</field>
                </record>
                <record model="res.users" id="base.user_demo">
                    <field name="login">demo</field>
                    <field name="name">Marc Demo</field>
                    <field name="lang">en_US</field>
                </record>
                <record model="res.users" id="base.user_admin">
                    <field name="login">admin</field>
                    <field name="name">Mitchell Admin</field>
                    <field name="lang">en_US</field>
                </record>
            </odoo>
            """,
        )

    def test_03_user_export(self):
        # create groups not related to any existing group, since because of implied
        # groups, the result could be different depending on the modules installed and
        # their dependencies
        fake_group1 = self.env["res.groups"].create({"name": "Fake Group #1"})
        fake_group1._ensure_human_xml_id()
        fake_group2 = self.env["res.groups"].create({"name": "Fake Group #2"})
        fake_group2._ensure_human_xml_id()
        model = self.env["res.users"]
        user = model.create(
            {
                "email": "testuser@testuser.com",
                "groups_id": [
                    Command.set(
                        [
                            fake_group1.id,
                            fake_group2.id,
                        ]
                    )
                ],
                "name": "Test User",
                "login": "testuser",
                "password": "testuser",
            }
        )
        child1 = self.env["res.partner"].create(
            {"name": "Child Contact #1", "parent_id": user.partner_id.id}
        )
        child2 = self.env["res.partner"].create(
            {"name": "Child Contact #2", "parent_id": user.partner_id.id}
        )
        # Ensure the user has a human-readable XML ID otherwise the field will
        # be exported with a search attribute:
        # <field name="commercial_partner_id" model="res.partner" search="[('name', '=', 'Test User')]"/>  # noqa: E501
        user.commercial_partner_id._ensure_human_xml_id()
        export = self.export(
            model,
            fields=[
                "login",  # test a char field
                "name",  # test a char field
                "lang",  # test a selection field
                "groups_id",  # test a many2many field
                "commercial_partner_id",  # test a many2one field
                "employee",  # test a boolean field
                "child_ids/name",  # test a one2many field
            ],
            params={"ids": user.ids},
        )
        self.assertExportEqual(
            export,
            f"""
            <?xml version="1.0" ?>
            <odoo>
                <record model="res.partner" id="res_partner_{child1.id}__child_contact_1">
                    <field name="name">Child Contact #1</field>
                </record>
                <record model="res.partner" id="res_partner_{child2.id}__child_contact_2">
                    <field name="name">Child Contact #2</field>
                </record>
                <record model="res.users" id="res_users_{user.id}__test_user">
                    <field name="login">testuser</field>
                    <field name="name">Test User</field>
                    <field name="lang">en_US</field>
                    <field name="groups_id" eval="[
                            Command.link(ref('xml_export.res_groups_{fake_group1.id}__fake_group_1')),
                            Command.link(ref('xml_export.res_groups_{fake_group2.id}__fake_group_2'))
                        ]"/>
                    <field name="commercial_partner_id" ref="xml_export.res_partner_{user.commercial_partner_id.id}__test_user"/>
                    <field name="employee" eval="False"/>
                    <field name="child_ids" eval="[
                            Command.link(ref('res_partner_{child1.id}__child_contact_1')),
                            Command.link(ref('res_partner_{child2.id}__child_contact_2'))
                        ]"/>
                </record>
            </odoo>
            """,  # noqa: E501
        )
