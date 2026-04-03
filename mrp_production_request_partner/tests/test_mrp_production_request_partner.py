# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestMrpProductionRequestPartnerCommon


class TestMrpProductionRequestPartner(TestMrpProductionRequestPartnerCommon):
    """Tests for mrp_production_request_partner module."""

    def test_01_create_request_without_sale_order(self):
        """Creating a request without sale_order_id leaves partner_id empty."""
        request = self.RequestModel.create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
            }
        )
        self.assertFalse(request.partner_id)

    def test_02_create_request_with_sale_order(self):
        """Creating a request with sale_order_id auto-sets partner_id."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        request = self.RequestModel.create(
            {
                "product_id": self.product.id,
                "product_qty": 1.0,
                "bom_id": self.bom.id,
                "sale_order_id": sale_order.id,
            }
        )
        self.assertEqual(request.partner_id, sale_order.partner_shipping_id)

    def test_03_wizard_prepare_mo_includes_partner(self):
        """Wizard _prepare_manufacturing_order includes partner_id from request."""
        request = self.RequestModel.create(
            {
                "product_id": self.product.id,
                "product_qty": 2.0,
                "bom_id": self.bom.id,
                "partner_id": self.partner.id,
            }
        )
        ctx = {
            "active_ids": request.ids,
            "active_model": request._name,
        }
        wizard = self.WizModel.with_context(**ctx).create({})
        vals = wizard._prepare_manufacturing_order()
        self.assertEqual(vals.get("partner_id"), self.partner.id)

    def test_04_form_view_fields(self):
        """Form view has partner_id and zip_id fields."""
        view_info = self.env["mrp.production.request"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("partner_id", field_names)
        self.assertIn("zip_id", field_names)

    def test_05_list_view_fields(self):
        """List view has partner_id and zip_id fields."""
        view_info = self.env["mrp.production.request"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("partner_id", field_names)
        self.assertIn("zip_id", field_names)

    def test_06_search_view_filters(self):
        """Search view has groupby_partner_id and groupby_zip_id filters."""
        view_info = self.env["mrp.production.request"].get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"])
        filter_names = [el.get("name") for el in arch.iter("filter")]
        self.assertIn("groupby_partner_id", filter_names)
        self.assertIn("groupby_zip_id", filter_names)
