# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import contextlib
from unittest.mock import Mock

import odoo
import odoo.http
from odoo.tests.common import TransactionCase


@contextlib.contextmanager
def MockRequest(env):
    """Simulate an Odoo HTTP request bound to the given environment."""
    mock = Mock(
        db=None,
        env=env,
        httprequest=Mock(files={}, remote_addr="127.0.0.1", host="localhost"),
        cookies={},
        params={},
        session={"force_website_id": False},
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(mock)
        s.callback(odoo.http._request_stack.pop)
        yield mock


class TestWebsiteContactCommon(TransactionCase):
    """Base class with shared fixtures for website_contact tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.HelpdeskCategory = cls.env["helpdesk.ticket.category"]
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]
        cls.CrmLead = cls.env["crm.lead"]
        cls.category = cls.HelpdeskCategory.create(
            {
                "name": "Test Category",
                "sequence": 10,
                "public_filter": "test_filter",
            }
        )
