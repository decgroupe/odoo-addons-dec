# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_convert_to_helpdesk_ticket(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "crm_lead_to_helpdesk_ticket.act_crm_lead_to_helpdesk_ticket"
        )
        return action
