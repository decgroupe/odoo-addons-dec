# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleReportQwebCommon(TransactionCase):
    """Common base class for sale_report_qweb tests."""

    def setUp(self):
        """Set up shared test data."""
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Customer"})  # type: ignore[index]
        self.tax = self.env["account.tax"].create(  # type: ignore[index]
            {
                "name": "Test Sale Tax",
                "amount_type": "percent",
                "amount": 15.0,
                "type_tax_use": "sale",
            }
        )
        self.product = self.env["product.product"].create(  # type: ignore[index]
            {
                "name": "Test Product",
                "type": "consu",
                "taxes_id": [Command.link(self.tax.id)],
            }
        )

    def _create_sale_order(self):
        """Create a sale order that exercises the custom report template."""
        return self.env["sale.order"].create(  # type: ignore[index]
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Test Section",
                        }
                    ),
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 2.0,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 100.0,
                            "discount": 10.0,
                            "tax_id": [Command.link(self.tax.id)],
                        }
                    ),
                ],
            }
        )

    def _render_sale_report_html(self, sale_order):
        """Render the sale order report HTML for a sale order."""
        html = self.env["ir.actions.report"]._render_qweb_html(
            "sale.report_saleorder", sale_order.ids
        )[0]  # pyright: ignore[reportPrivateUsage]
        return html.decode() if isinstance(html, bytes) else html
