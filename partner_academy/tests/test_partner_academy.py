# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests import Form, common


class TestPartnerAcademy(common.TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_email_onchange_set_academy_single_domain(self):
        new_partner = Form(self.env["res.partner"])
        new_partner.name = "Teacher"
        new_partner.email = "teacher@ac-nantes.fr"
        self.assertEqual(
            new_partner.academy_id,
            self.env.ref("partner_academy.aca_nantes"),
        )

    def test_02_email_onchange_set_academy_multiple_domain(self):
        for domain in ("ac-caen.fr", "ac-rouen.fr", "ac-normandie.fr"):
            new_partner = Form(self.env["res.partner"])
            new_partner.email = "teacher@%s" % (domain)
            self.assertEqual(
                new_partner.academy_id,
                self.env.ref("partner_academy.aca_normandie_rouen_caen"),
            )
