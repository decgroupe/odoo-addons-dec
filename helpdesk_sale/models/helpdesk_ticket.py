# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from markupsafe import Markup
from werkzeug.urls import url_encode

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def close(self):
        stage_done = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        for ticket in self:
            ticket.stage_id = stage_done

    def action_create_quotation(self):
        ticket_action = self.env.ref("helpdesk_mgmt.helpdesk_ticket_action").sudo()
        quot_action = self.env.ref("sale.action_quotations_with_onboarding").sudo()
        # Reset the context to avoid team_id collision when creating a new sale order
        default_context = self.env.user.context_get()
        # pylint: disable=W8121
        Order = self.env["sale.order"].with_context(default_context)
        # initialize result dict
        res = {}
        for ticket in self:
            res.setdefault(ticket.id, False)
        # process creating a sale order for each ticket
        # and update the result dict with the order id
        for ticket in self:
            so_data = {
                "summary": self.env._(
                    "Case %(number)s: %(name)s",
                    number=ticket.number,
                    name=ticket.name,
                ),
                "origin": ticket.number,
                "partner_id": ticket.partner_id and ticket.partner_id.id or False,
                "date_order": fields.Date.today(),
            }
            order_id = Order.create(so_data)
            res[ticket.id] = order_id.id

            # Create a ref to sale_order to ticket references
            tickref_data = {
                "ticket_id": ticket.id,
                "model_ref_id": f"sale.order,{order_id.id}",
            }
            _tickref_id = self.env["helpdesk.ticket.reference"].create(tickref_data)

            # Post a note with a reference to the ticket
            body = self.env._(
                "Created from helpdesk ticket <a href='/web?#%(url)s'>%(name)s</a>",
                url=url_encode(
                    {
                        "id": ticket.id,
                        "model": "helpdesk.ticket",
                        "action": ticket_action.id,
                        "view_type": "form",
                    }
                ),
                name=ticket.number,
            )
            order_id.message_post(body=Markup(body))

            # Post a note with a reference to the quotation
            body = self.env._(
                "New quotation <a href='/web?#%(url)s'>%(name)s</a> created",
                url=url_encode(
                    {
                        "id": order_id.id,
                        "model": "sale.order",
                        "action": quot_action.id,
                        "view_type": "form",
                    }
                ),
                name=order_id.name,
            )
            ticket.message_post(body=Markup(body))
            # Close ticket
            ticket.close()
        return res
