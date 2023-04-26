# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from ast import literal_eval

from odoo.tests import common


@common.tagged("-at_install", "post_install")
class TestMassEditingChat(common.SavepointCase):
    """ """

    def setUp(self):
        super().setUp()
        self.mass_editing_partner_note = self.env.ref(
            "mass_editing_chat.mass_editing_partner_note"
        )

    def _create_wizard_and_apply_values(self, server_action, items, vals):
        action = server_action.with_context(
            active_model=items._name,
            active_ids=items.ids,
        ).run()
        wizard = (
            self.env[action["res_model"]]
            .with_context(
                literal_eval(action["context"]),
            )
            .create(vals)
        )
        wizard.button_apply()
        return wizard

    def test_mass_edit_partner_note(self):
        partner_ids = (
            self.env.ref("base.res_partner_address_15")
            + self.env.ref("base.res_partner_address_16")
            + self.env.ref("base.res_partner_address_28")
        )
        chat_message = "FYI: I have added a warning message for this contact"
        vals = {
            "selection__comment": "set",
            "comment": "Do not send private messages to this contact",
            "chat_message": chat_message,
        }
        self._create_wizard_and_apply_values(
            self.mass_editing_partner_note, partner_ids, vals
        )
        for partner_id in partner_ids:
            self.assertIn(chat_message, partner_id.message_ids[0].body)
