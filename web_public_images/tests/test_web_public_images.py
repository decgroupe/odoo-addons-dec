# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import tagged

from odoo.addons.web_public_images.tests.common import (
    TestWebPublicImagesBase,
)


@tagged("-at_install", "post_install")
class TestWebPublicImages(TestWebPublicImagesBase):
    """Test web_public_images module"""

    def setUp(self):
        super().setUp()

    def test_01_get_partner_avatar(self):
        # brandon.freeman55@example.com
        partner_id = self.env.ref("base.res_partner_address_15")
        # test GET
        res = self.url_open(f"/web/image/res.partner/{partner_id.id}/avatar_128")
        # placeholder or not, the image must be served correctly
        self.assertEqual(res.status_code, 200)
        # note that we cannot compare image directly because of image crop/resize and
        # other optimization that can be applied on-the-fly by odoo.
        # only response headers can be checked reliably here.
        self.assertIn(
            "128x128-crop=False-quality=0",
            res.headers["ETag"],
        )
        self.assertNotIn(
            "filename=placeholder.png",
            res.headers["Content-Disposition"],
        )
        self.assertIn(
            'filename="Brandon Freeman.jpg"',
            res.headers["Content-Disposition"],
        )
