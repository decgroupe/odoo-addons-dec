# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025


import odoo.tests


@odoo.tests.tagged("post_install", "-at_install")
class TestSoftwareLicenseTokenHttp(odoo.tests.HttpCase):

    def setUp(self):
        super().setUp()

    def _get_attachment(self, hardware_id):
        domain = [
            ("res_model", "=", hardware_id._name),
            ("res_id", "=", hardware_id.id),
        ]
        attachment_ids = self.env["ir.attachment"].search(domain)
        return attachment_ids

    def test_01_download_license_file(self):
        brickgame_lic1 = self.env.ref("software_license.sl_brickgame1")
        self.assertEqual(brickgame_lic1.get_remaining_activation(), 1)
        added_hardware_id = brickgame_lic1.activate("9d:24:26:52:12:81")
        action = added_hardware_id.action_download_license_file()
        self.assertEqual(
            action["type"],
            "ir.actions.act_url",
        )
        attachment_id = self._get_attachment(added_hardware_id)[0]
        self.assertEqual(
            action["url"],
            "/web/content/%d?download=true" % attachment_id.id,
        )
        res_binary = self.url_open(action["url"])
        # real status is 403 but this route hookthe result using `_response_by_status`
        self.assertEqual(res_binary.status_code, 404)
        # for public access, we need an access token
        attachment_id.generate_access_token()
        public_url = action["url"] + "&access_token=%s" % attachment_id.access_token
        res_binary = self.url_open(public_url)
        self.assertEqual(res_binary.status_code, 200)
