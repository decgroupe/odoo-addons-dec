# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from odoo import Command

from odoo.addons.mail_extra_notify.tests.common import TestMailExtraNotifyCommon, tagged


@tagged("post_install", "-at_install")
class TestMailExtraNotifyProject(TestMailExtraNotifyCommon):
    """Test the extra information in the email body for project-related
    notifications."""

    def setUp(self):
        super().setUp()
        city_id = self.env["res.city"].create(
            {
                "name": "Test City",
                "country_id": self.env.ref("base.fr").id,
            }
        )
        zip_id = self.env["res.city.zip"].create(
            {
                "name": "53000",
                "city_id": city_id.id,
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "zip_id": zip_id.id,
            }
        )
        service = self.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
            }
        )
        sale_order_id = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": service.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        project_id = self.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )
        self.task_id = self.env["project.task"].create(
            {
                "name": "Furniture",
                "project_id": project_id.id,
                "sale_line_id": sale_order_id.order_line[0].id,
            }
        )

    def test_01_assigned_sheet_more_informations(self):
        with self.patch_mail_unlink():
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # set salesperson
            self.task_id.user_ids = [Command.set([self.user1.id])]
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "You have been assigned to Furniture",
            )
            self.assertIn("Sales Order Item", mail_id.body)
            self.assertIn("Shipping Partner", mail_id.body)
            self.assertIn("Shipping Partner's ZIP", mail_id.body)

    def test_02_assigned_activity_more_informations(self):
        with self.patch_mail_unlink():
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # assign an activity
            _activity_id = self.task_id.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                note="Please check this",
                user_id=self.user1.id,
            )
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                '"Furniture: To-Do" assigned to you',
            )
            self.assertIn("Sales Order Item", mail_id.body)
            self.assertIn("Shipping Partner", mail_id.body)
            self.assertIn("Shipping Partner's ZIP", mail_id.body)
