# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo.tests.common import tagged

from .common import TestMrpStageBase


@tagged("post_install", "-at_install")
class TestMrpStage(TestMrpStageBase):
    """Tests for mrp_stage module."""

    def test_01_validate_mo_states(self):
        """Tests that all hard-coded manufacturing order states have a stage match"""
        state_field = self.production_model._fields["state"]
        mo_states = [s[0] for s in state_field.selection]
        stages = self.production_model._get_stages_ref()
        for state in mo_states:
            self.assertIn(state, stages)
