# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import base64
import json

import odoo.http as http
from odoo import SUPERUSER_ID, _, tools
from odoo.addons.tools_miscellaneous.tools.html_helper import b, p
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


URL_BASE = "/contact"

# Because of ./odoo/addons/website_form/static/src/snippets/s_website_form/000.js
# In the `send` function the attachment field is split into multiple fields, the first
# index is for the case when multiple fields with the same name would exists in the same
# form, the second index is for when multiple files are attached.
ATTACHMENT_IDX = "attachment[%d][%d]"
ATTACHMENT_000_NAME = ATTACHMENT_IDX % (0, 0)


class WebsiteContactController(http.Controller):
    """Http Controller for Contact Forms"""

    #######################################################################

    def _get_origins(self):
        return {
            "private": _("A private person"),
            "school": _("A school"),
            "company": _("A company "),
        }

    def _get_company_label(self, origin):
        if origin == "school":
            res = _("School")
        elif origin == "company":
            res = _("Company")
        else:
            res = False
        return res

    def _get_description(self):
        res = _("Company Name") + ":\n- \n"
        res += _("Full Address (street, zipcode, city)") + ":\n- \n"
        res += _("Your Request") + ":\n- \n"
        return res

    def _save_attachments(self, model, id, public=False):
        IrAttachment = request.env["ir.attachment"]
        attachment_ids = IrAttachment
        # We browse files directly without `.getlist("inputname")`
        for file in request.httprequest.files:
            c_file = request.httprequest.files[file]
            data = c_file.read()
            if c_file.filename:
                attachment_ids += IrAttachment.sudo().create(
                    {
                        "name": c_file.filename,
                        "datas": base64.b64encode(data),
                        "res_model": model,
                        "res_id": id,
                    }
                )
            if public:
                attachment_ids.sudo().generate_access_token()

    #######################################################################

    @http.route(
        URL_BASE + "/ticket/new/<string:filter>",
        type="http",
        auth="public",
        website=True,
    )
    def create_new_ticket_from_contactform(self, filter, **kw):
        categories = http.request.env["helpdesk.ticket.category"].search(
            [("active", "=", True), ("public_filter", "=", filter)]
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
                "submit_text": _("Submit"),
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
        try:
            # The except clause below should not let what has been done inside
            # here be committed. It should not either roll back everything in
            # this controller method. Instead, we use a savepoint to roll back
            # what has been done inside the try clause.
            with request.env.cr.savepoint():
                if request.env["ir.http"]._verify_request_recaptcha_token(
                    "website_form"
                ):
                    return self._handle_submit_ticket_from_contactform(**kw)
            error = _("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({"error": error})

    def _handle_submit_ticket_from_contactform(self, **kw):
        channel_id = (
            request.env["helpdesk.ticket.channel"].sudo().search([("name", "=", "Web")])
        )
        partner_id = (
            request.env["res.partner"]
            .sudo()
            .search([("email", "ilike", kw.get("email"))], limit=1)
        )
        team_id = request.env["helpdesk.ticket.team"].sudo()
        category = kw.get("category")
        if category:
            team_ids = team_id.search([("category_ids", "in", [category])])
            if len(team_ids) == 1:
                # Assign `team_id` if there is one and only one match
                team_id = team_ids[0]
        if kw.get("description"):
            desc = {
                _("Origin"): self._get_origins().get(kw.get("origin"), ""),
                _("Message"): tools.plaintext2html(kw.get("description")),
                _("References"): kw.get("references"),
            }
            description = ""
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
        return http.request.render(
            "website_contact.create_contact_message",
            {
                "show_origin_form_group": True,
                "show_email_form_group": True,
                "origin": self._get_origins(),
                "submit_text": _("Next"),
                "form_action": URL_BASE + "/lead/next",
                "force_action": "",
                "success_mode": "",
                "success_page": "",
            },
        )

    @http.route(URL_BASE + "/lead/next", type="http", auth="public", website=True)
    def create_new_lead_from_contactform2(self, **kw):
        partner_id = (
            request.env["res.partner"]
            .sudo()
            .search([("email", "ilike", kw.get("email"))], limit=1)
        )
        company_label = self._get_company_label(kw.get("origin"))
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
                "email": kw.get("email"),
                "description": "",
                "partner_id": partner_id.id,
                "partner_name": partner_id.name,
                "submit_text": _("Submit"),
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
        try:
            # The except clause below should not let what has been done inside
            # here be committed. It should not either roll back everything in
            # this controller method. Instead, we use a savepoint to roll back
            # what has been done inside the try clause.
            with request.env.cr.savepoint():
                if request.env["ir.http"]._verify_request_recaptcha_token(
                    "website_form"
                ):
                    return self._handle_submit_lead_from_contactform(**kw)
            error = _("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({"error": error})

    def _handle_submit_lead_from_contactform(self, **kw):
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
