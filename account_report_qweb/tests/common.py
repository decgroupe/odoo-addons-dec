# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAccountReportQwebCommon(TransactionCase):
    """Common base class for account_report_qweb tests."""

    def setUp(self):
        """Set up shared test data."""
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Customer"})  # type: ignore[index]
        self.tax = self.env["account.tax"].create(  # type: ignore[index]
            {
                "name": "Test Invoice Tax",
                "amount_type": "percent",
                "amount": 15.0,
                "type_tax_use": "sale",
            }
        )
        self.income_account = self.env["account.account"].search(  # type: ignore[index]
            [("account_type", "=", "income")], limit=1
        )

    def _create_invoice(self):
        """Create an invoice that exercises the custom report template."""
        return self.env["account.move"].create(  # type: ignore[index]
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Services",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Consulting",
                            "quantity": 2.0,
                            "price_unit": 100.0,
                            "discount": 10.0,
                            "account_id": self.income_account.id,
                            "tax_ids": [Command.link(self.tax.id)],
                        }
                    ),
                ],
            }
        )

    def _render_invoice_report_html(self, invoice):
        """Render the invoice report HTML for an account move."""
        html = self.env["ir.actions.report"]._render_qweb_html(  # pyright: ignore[reportPrivateUsage]
            "account.report_invoice", invoice.ids
        )[0]
        return html.decode() if isinstance(html, bytes) else html
