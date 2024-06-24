# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmLeadToHelpdeskTicket(models.TransientModel):
    _name = "crm.lead.to.helpdesk.ticket"
    _description = "Convert Lead to Helpdesk Ticket"

    lead_id = fields.Many2one("crm.lead", "Associated Lead")
    lead_close = fields.Boolean(
        string="Close",
        help="Close this lead immediatly (mark as lost)",
        default=True,
    )
    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True, sanitize_style=True)
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        index=True,
        domain="team_id and [('share', '=', False),('id', 'in', user_ids)] "
        "or [('share', '=', False)]",
    )
    user_ids = fields.Many2many(
        comodel_name="res.users", related="team_id.user_ids", string="Users"
    )
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    partner_name = fields.Char()
    partner_email = fields.Char(string="Email")
    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        string="Ticket",
    )

    @api.model
    def default_get(self, fields):
        result = super(CrmLeadToHelpdeskTicket, self).default_get(fields)
        active_id = self._context.get("active_id")
        active_model = self._context.get("active_model")
        if active_model == "crm.lead" and active_id:
            lead_id = self.env["crm.lead"].browse(active_id)[0]
            result["lead_id"] = lead_id.id
            if not "name" in result:
                result["name"] = lead_id.name
            if not "description" in result:
                result["description"] = lead_id.description
                if not result["description"] and lead_id.original_message_id.body:
                    result["description"] = "<u>%s:</u> <blockquote>%s</blockquote>" % (
                        lead_id.original_message_id.email_from,
                        lead_id.original_message_id.body,
                    )
            if not "partner_id" in result:
                result["partner_id"] = lead_id.partner_id.id
            if not "partner_name" in result:
                result["partner_name"] = lead_id.partner_name
            if not "partner_email" in result:
                result["partner_email"] = lead_id.email_from
                if not result["partner_email"]:
                    result["partner_email"] = lead_id.original_message_id.email_from
        return result

    def _get_ticket_create_data(self):
        return {
            "name": self.name,
            "description": self.description,
            "category_id": self.category_id.id,
            "user_id": self.user_id.id,
            "team_id": self.team_id.id,
            "partner_id": self.partner_id.id,
            "partner_name": self.partner_name,
            "partner_email": self.partner_email,
        }

    def action_create_ticket(self):
        HelpdeskTicket = self.env["helpdesk.ticket"]
        if not self.team_id and not self.user_id:
            raise ValidationError(_("A user (or at least a team) is required!"))
        if not self.partner_email and not self.partner_id.email:
            raise ValidationError(_("An email is required!"))
        if self.user_id:
            HelpdeskTicket = HelpdeskTicket.with_user(self.user_id)
        # soft support for `helpdesk_notify` module
        self.ticket_id = HelpdeskTicket.with_context(force_helpdesk_notify=True).create(
            self._get_ticket_create_data()
        )
        if self.user_id:
            # restore original user
            self.ticket_id = self.ticket_id.with_user(self.env.user)
            # force sending a "You have been assigned" notification since odoo will
            # not do it (because the ticket will be created by this same user)
            self.ticket_id._message_auto_subscribe_notify(
                [self.user_id.partner_id.id], "mail.message_user_assigned"
            )
        self._message_post_ticket_created_messages(self.ticket_id, self.lead_id)
        if self.lead_id and self.lead_close:
            self.lead_id.action_set_lost()
        return self._action_view_ticket(self.ticket_id)

    def _message_post_ticket_created_messages(self, ticket_id, lead_id):
        if ticket_id and lead_id:
            # post message on ticket
            msg = _("This ticket has been created from: ") + (
                "<a href=# data-oe-model=crm.lead data-oe-id=%d>%s</a>"
            ) % (lead_id.id, lead_id.display_name)
            ticket_id.message_post(body=msg)
            # post message back on lead
            msg = _("A new ticket has been created: ") + (
                "<a href=# data-oe-model=helpdesk.ticket data-oe-id=%d>%s</a>"
            ) % (ticket_id.id, ticket_id.display_name)
            lead_id.message_post(body=msg)

    def _action_view_ticket(self, ticket_id):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "helpdesk_mgmt.action_helpdesk_ticket_kanban_from_dashboard"
        )
        form_view_id = self.env.ref("helpdesk_mgmt.ticket_view_form", False)
        form_view = [(form_view_id and form_view_id.id or False, "form")]
        if "views" in action:
            action["views"] = form_view + [
                (state, view) for state, view in action["views"] if view != "form"
            ]
        else:
            action["views"] = form_view
        action["res_id"] = ticket_id.id
        return action
