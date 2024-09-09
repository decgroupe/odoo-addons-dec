# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests import SavepointCase
from odoo.tests.common import Form


class TestSaleInvoiceRate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Partners
        res_partner_obj = cls.env["res.partner"]
        product_obj = cls.env["product.product"]
        cls.res_partner_1 = res_partner_obj.create({"name": "Test Partner 1"})
        # Taxes
        tax_obj = cls.env["account.tax"]
        cls.tax_18p = tax_obj.create(
            {
                "name": "Tax 18%",
                "amount": 18.0,
            }
        )
        # Products
        cls.product_1 = product_obj.create(
            {
                "name": "Desk Combination 1",
                "type": "consu",
                "invoice_policy": "order",
                "taxes_id": [(6, 0, cls.tax_18p.ids)],
            }
        )
        cls.product_2 = product_obj.create(
            {
                "name": "Desk Combination 2",
                "type": "consu",
                "invoice_policy": "delivery",
                "taxes_id": [(6, 0, cls.tax_18p.ids)],
            }
        )
        # Sale Order
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )

    def test_01_add_product(self):
        """Check add product to sale order"""
        with Form(self.sale_order_1) as form:
            with form.order_line.new() as line_1:
                line_1.product_id = self.product_1
                line_1.price_unit = 100.0
            with form.order_line.new() as line_2:
                line_2.product_id = self.product_2
                line_2.price_unit = 150.0

        sale_order = form.save()
        # amount to invoice must be equal 0
        self.assertEqual(sale_order.amount_to_invoice_ordqty_taxexcl, 0)
        self.assertEqual(sale_order.amount_to_invoice_ordqty_taxincl, 0)
        sale_order.action_confirm()
        # amount to invoice must be equal 250.0 (295 w/taxes) whatever delivered
        # quantities and product's `invoice_policy`
        self.assertEqual(sale_order.amount_to_invoice_ordqty_taxexcl, 250.0)
        self.assertEqual(sale_order.amount_to_invoice_ordqty_taxincl, 295.0)
        sale_order.order_line[1].qty_delivered = 1
        self.assertEqual(sale_order.amount_to_invoice_ordqty_taxexcl, 250.0)
        self.assertEqual(sale_order.amount_to_invoice_ordqty_taxincl, 295.0)
