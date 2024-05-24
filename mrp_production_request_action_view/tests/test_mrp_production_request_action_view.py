# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from .common import TestMrpProductionRequestActionViewCommon


class TestMrpProductionRequestActionView(TestMrpProductionRequestActionViewCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_production_request_action_view(self):
        self._test_action_view_sm_records(self.model_production_request)
