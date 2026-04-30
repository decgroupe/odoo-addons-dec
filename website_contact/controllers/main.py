# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import base64
import json

import odoo.http as http
from odoo import SUPERUSER_ID, tools
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from odoo.addons.tools_miscellaneous.tools.html_helper import b, p

URL_BASE = "/contact"

# because of the website form js, the attachment field is split into multiple fields:
# the first index is for when multiple fields with the same name exist in the same form,
# the second index is for when multiple files are attached.
ATTACHMENT_IDX = "attachment[%d][%d]"
ATTACHMENT_000_NAME = ATTACHMENT_IDX % (0, 0)


class WebsiteContactController(http.Controller):
    """Http Controller for Contact Forms"""

    #######################################################################

    def _get_origins(self):
        """Return a dict mapping origin keys to their translated labels."""
        return {
            "private": request.env._("A private person"),
            "school": request.env._("A school"),
            "company": request.env._("A company "),
        }

    def _get_company_label(self, origin):
        """Return the translated company label for the given origin, or False."""
        if origin == "school":
            res = request.env._("School")
        elif origin == "company":
            res = request.env._("Company")
        else:
            res = False
        return res

    def _get_description(self):
        """Return a default description template with translated field labels."""
        res = request.env._("Company Name") + ":\n- \n"
        res += request.env._("Full Address (street, zipcode, city)") + ":\n- \n"
        res += request.env._("Your Request") + ":\n- \n"
        return res

    def _save_attachments(self, model, record_id, public=False):
        """Save uploaded files as attachments linked to the given model record."""
        IrAttachment = request.env["ir.attachment"]
        attachment_ids = IrAttachment
        # browse files directly without `.getlist("inputname")`
        for file in request.httprequest.files:
            c_file = request.httprequest.files[file]
            data = c_file.read()
            if c_file.filename:
                attachment_ids += IrAttachment.sudo().create(
                    {
                        "name": c_file.filename,
                        "datas": base64.b64encode(data),
                        "res_model": model,
                        "res_id": record_id,
                    }
                )
            if public:
                attachment_ids.sudo().generate_access_token()

    #######################################################################

    @http.route(
        URL_BASE + "/ticket/new/<string:ticket_filter>",
        type="http",
        auth="public",
        website=True,
    )
    def create_new_ticket_from_contactform(self, ticket_filter, **kw):
        """Render the contact form for creating a new helpdesk ticket."""
        categories = http.request.env["helpdesk.ticket.category"].search(
            [("active", "=", True), ("public_filter", "=", ticket_filter)]
        )
        return http.request.render(
            "website_contact.create_contact_message",
            {
                "origin": self._get_origins(),
                "categories": categories,
                "description": self._get_description(),
                "show_origin_form_group": True,
                "show_email_form_group": True,
                "show_company_form_group": False,
                "show_name_form_group": True,
                "show_function_form_group": False,
                "show_phone_mobile_form_group": False,
                "show_address_form_group": False,
                "show_category_form_group": True,
                "show_subject_form_group": True,
                "show_description_form_group": True,
                "show_references_form_group": True,
                "show_attachment_form_group": True,
                "submit_text": request.env._("Submit"),
                "form_action": URL_BASE + "/ticket/submit",
                "force_action": "",
                "success_mode": "redirect",
                "success_page": "/contactus-thank-you",
            },
        )

    @http.route(
        URL_BASE + "/ticket/submit", type="http", auth="public", website=True, csrf=True
    )
    def submit_ticket_from_contactform(self, **kw):
        """Submit the contact form and create a helpdesk ticket if recaptcha passes."""
        try:
            # the except clause below should not let what has been done inside
            # here be committed. it should not either roll back everything in
            # this controller method. instead, we use a savepoint to roll back
            # what has been done inside the try clause.
            with request.env.cr.savepoint():
                if request.env["ir.http"]._verify_request_recaptcha_token(
                    "website_form"
                ):
                    return self._handle_submit_ticket_from_contactform(**kw)
            error = request.env._("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({"error": error})

    def _handle_submit_ticket_from_contactform(self, **kw):
        """Create a helpdesk ticket from the submitted contact form data."""
        channel_id = (
            request.env["helpdesk.ticket.channel"].sudo().search([("name", "=", "Web")])
        )
        partner_id = (
            request.env["res.partner"]
            .sudo()
            .search([("email", "ilike", kw.get("email"))], limit=1)
        )
        team_id = request.env["helpdesk.ticket.team"].sudo()
        category = int(kw.get("category", 0))
        if category:
            team_ids = team_id.search([("category_ids", "in", [category])])
            if len(team_ids) == 1:
                # Assign `team_id` if there is one and only one match
                team_id = team_ids[0]
        description = ""
        if kw.get("description"):
            desc = {
                request.env._("Origin"): self._get_origins().get(kw.get("origin"), ""),
                request.env._("Message"): tools.plaintext2html(kw.get("description")),
                request.env._("References"): kw.get("references"),
            }
            for head in desc:
                if desc[head]:
                    description += p(b(head + ":") + "<br/>" + desc[head])
        vals = {
            "partner_name": kw.get("name"),
            "company_id": request.env.user.company_id.id,
            "category_id": category,
            "team_id": team_id.id,
            "user_id": False,
            "partner_email": kw.get("email"),
            "description": description,
            "name": kw.get("subject"),
            "attachment_ids": False,
            "channel_id": channel_id.id,
            "partner_id": partner_id.id,
        }
        # Create the ticket
        ticket_id = (
            request.env["helpdesk.ticket"]
            .with_user(SUPERUSER_ID)
            .with_context(contact_ticket=True)
            .create(vals)
        )
        # And subscribe the partner if retrieved from email
        if partner_id:
            ticket_id.message_subscribe(partner_ids=partner_id.ids)
        if kw.get(ATTACHMENT_000_NAME):
            self._save_attachments("helpdesk.ticket", ticket_id.id, True)
        return json.dumps({"id": ticket_id.id})

    #######################################################################

    @http.route(URL_BASE + "/lead/new", type="http", auth="public", website=True)
    def create_new_lead_from_contactform1(self, **kw):
        """Render the first step of the lead creation contact form."""
        return http.request.render(
            "website_contact.create_contact_message",
            {
                "show_origin_form_group": True,
                "show_email_form_group": True,
                "origin": self._get_origins(),
                "submit_text": request.env._("Next"),
                "form_action": URL_BASE + "/lead/new/save",
                "force_action": "",
                "success_mode": "redirect",
                "success_page": URL_BASE + "/lead/next",
            },
        )

    @http.route(
        URL_BASE + "/lead/new/save", type="http", auth="public", website=True, csrf=True
    )
    def create_new_lead_from_contactform2(self, **kw):
        """Store form data in session and return JSON to trigger JS redirect."""
        request.session["wc_lead_email"] = kw.get("email", "")
        request.session["wc_lead_origin"] = kw.get("origin", "")
        return json.dumps({"id": 1})

    @http.route(URL_BASE + "/lead/next", type="http", auth="public", website=True)
    def create_new_lead_from_contactform3(self, **kw):
        """Render the second step of the lead creation contact form from session."""
        email = request.session.get("wc_lead_email", "")
        origin = request.session.get("wc_lead_origin", "")
        if not email and not origin:
            return http.request.redirect(URL_BASE + "/lead/new")
        partner_id = (
            request.env["res.partner"]
            .sudo()
            .search([("email", "ilike", email)], limit=1)
        )
        company_label = self._get_company_label(origin)
        return http.request.render(
            "website_contact.create_contact_message",
            {
                "company_label": company_label,
                "show_company_form_group": partner_id.id is False
                and company_label is not False,
                "show_name_form_group": partner_id.id is False,
                "show_function_form_group": partner_id.id is False
                and company_label is not False,
                "show_phone_mobile_form_group": partner_id.id is False,
                "show_address_form_group": partner_id.id is False,
                "show_category_form_group": False,
                "show_subject_form_group": True,
                "show_description_form_group": True,
                "show_attachment_form_group": partner_id.id is not False,
                "email": email,
                "description": "",
                "partner_id": partner_id.id,
                "partner_name": partner_id.name,
                "submit_text": request.env._("Submit"),
                "form_action": URL_BASE + "/lead/submit",
                "force_action": "",
                "success_mode": "redirect",
                "success_page": "/contactus-thank-you",
            },
        )

    @http.route(
        URL_BASE + "/lead/submit", type="http", auth="public", website=True, csrf=True
    )
    def submit_lead_from_contactform(self, **kw):
        """Submit the contact form and create a CRM lead if recaptcha passes."""
        try:
            # the except clause below should not let what has been done inside
            # here be committed. it should not either roll back everything in
            # this controller method. instead, we use a savepoint to roll back
            # what has been done inside the try clause.
            with request.env.cr.savepoint():
                if request.env["ir.http"]._verify_request_recaptcha_token(
                    "website_form"
                ):
                    return self._handle_submit_lead_from_contactform(**kw)
            error = request.env._("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({"error": error})

    def _handle_submit_lead_from_contactform(self, **kw):
        """Create a CRM lead from the submitted contact form data."""
        description = kw.get("description")
        if description and kw.get("origin"):
            description = kw.get("origin") + "\n" + description
        utm_source_id = request.env.ref("website_contact.utm_source_contact_form")
        partner_id = kw.get("partner_id", False)
        if partner_id:
            partner_id = int(kw.get("partner_id"))
        vals = {
            "contact_name": kw.get("name"),
            "company_id": request.env.user.company_id.id,
            "user_id": False,
            "description": description,
            "name": kw.get("subject"),
            "attachment_ids": False,
            "partner_id": partner_id,
            "source_id": utm_source_id.id,
        }
        if not partner_id:
            vals.update(
                {
                    "street": kw.get("street"),
                    "city": kw.get("city"),
                    "zip": kw.get("zip"),
                    "partner_name": kw.get("company"),
                    "email_from": kw.get("email"),
                    "function": kw.get("function"),
                    "phone": kw.get("phone"),
                    "mobile": kw.get("mobile"),
                }
            )
        # Create the lead
        lead_id = (
            request.env["crm.lead"]
            .with_user(SUPERUSER_ID)
            .with_context(contact_lead=True)
            .create(vals)
        )
        # And subscribe the partner if retrieved from email
        if partner_id:
            lead_id.message_subscribe(partner_ids=[partner_id])
        if kw.get(ATTACHMENT_000_NAME):
            self._save_attachments("crm.lead", lead_id.id)
        return json.dumps({"id": lead_id.id})
