# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024


from odoo.tests.common import TransactionCase


class TestSoftwareApplication(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.release_model = self.env["software.application.release"]

    def test_01_portal_publish(self):
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        if fitness_app.portal_published:
            fitness_app.action_portal_publish()
            self.assertFalse(fitness_app.portal_published)
        if not fitness_app.portal_published:
            fitness_app.action_portal_publish()
            self.assertTrue(fitness_app.portal_published)
