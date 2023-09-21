# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from werkzeug.urls import url_encode

from odoo import _, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def close(self):
        stage_done = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        for ticket in self:
            ticket.stage_id = stage_done

    def action_create_quotation(self):
        ticket_action = self.env.ref("helpdesk_mgmt.helpdesk_ticket_action").sudo()
        quot_action = self.env.ref("sale.action_quotations_with_onboarding").sudo()
        # Reset the context to avoid team_id collision when creating a new
        # sale order
        default_context = self.env.user.context_get()
        Order = self.env["sale.order"].with_context(default_context)
        for ticket in self:
            data = {
                "summary": _("Case %s: %s") % (ticket.number, ticket.name),
                "origin": ticket.number,
                "partner_id": ticket.partner_id and ticket.partner_id.id or False,
                "date_order": fields.Date.today(),
            }
            order = Order.create(data)

            # Create a ref to sale_order to ticket references
            if order:
                data = {
                    "ticket_id": ticket.id,
                    "model_ref_id": "sale.order,{}".format(order.id),
                }
                self.env["helpdesk.ticket.reference"].create(data)

            # Post a note with a reference to the ticket
            body = _("Created from helpdesk ticket <a href='web#%s'>%s</a>") % (
                url_encode(
                    {
                        "id": ticket.id,
                        "model": "helpdesk.ticket",
                        "action": ticket_action.id,
                        "view_type": "form",
                    }
                ),
                ticket.number,
            )
            order.message_post(body=body)

            # Post a note with a reference to the quotation
            body = _("New quotation <a href='web#%s'>%s</a> created") % (
                url_encode(
                    {
                        "id": order.id,
                        "model": "sale.order",
                        "action": quot_action.id,
                        "view_type": "form",
                    }
                ),
                order.name,
            )
            ticket.message_post(body=body)
            # Close ticket
            ticket.close()
