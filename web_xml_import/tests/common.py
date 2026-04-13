# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestWebXmlImportCommon(TransactionCase):
    """Common base class for web_xml_import tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.XmlData = cls.env["xml.data"]
        # minimal valid Odoo XML data document
        cls.valid_xml_content = """<odoo>
    <data>
        <record model="res.lang" id="base.lang_en">
            <field name="name">English</field>
        </record>
    </data>
</odoo>"""
