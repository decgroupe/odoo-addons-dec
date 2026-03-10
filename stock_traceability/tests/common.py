# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestStockTraceabilityBase(TransactionCase):
    """Base class for Stock Traceability tests."""

    def _check_states(self, state_symbol_dict, model_name, field_name="state"):
        model = self.env[model_name]
        state_field = model._fields[field_name]
        states = [s[0] for s in state_field.selection]
        # ensure that all hard-coded states have a symbol match
        for state in states:
            self.assertIn(state, state_symbol_dict)
        # just check that no extra symbol is defined in the other way
        unknown_states = [s for s in state_symbol_dict.keys() if s not in states]
        if unknown_states:
            msg = f"`{model_name}` state symbol dict defined for unknown states:"
            for s in unknown_states:
                msg += f"\n\t- {s}"
            _logger.warning(msg)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
