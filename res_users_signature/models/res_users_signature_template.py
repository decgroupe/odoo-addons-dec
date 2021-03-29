# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

import copy
import functools
import datetime
import logging

from dateutil.relativedelta import relativedelta
from werkzeug import urls

from odoo import _, fields, models, api, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    mako_template_env.globals.update(
        {
            'str': str,
            'quote': urls.url_quote,
            'urlencode': urls.url_encode,
            'datetime': tools.wrap_module(datetime, []),
            'len': len,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'filter': filter,
            'reduce': functools.reduce,
            'map': map,
            'round': round,

            # dateutil.relativedelta is an old-style class and cannot be directly
            # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
            # is needed, apparently.
            'relativedelta': lambda *a, **kw: relativedelta(*a, **kw),
        }
    )
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class ResUsersSignatureTemplate(models.Model):
    _name = 'res.users.signature.template'
    _description = "Model used to store signature template and render "
    "html/text versions"

    name = fields.Char('Name')
    body_text = fields.Text(
        string='Text Version',
        help="Text version for reports",
    )
    body_html = fields.Html(
        string='Html Version',
        translate=True,
        sanitize=False,
    )
    body_lightweight_html = fields.Html(
        string='Lightweight Html Version',
        translate=True,
        sanitize=False,
    )

    def _render_template(self, template_txt, res_id):
        self.ensure_one()
        # try to load the template
        try:
            mako_env = mako_safe_template_env if self.env.context.get(
                'safe'
            ) else mako_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info(
                "Failed to load template %r", template_txt, exc_info=True
            )
            return False

        user = self.env['res.users'].browse(res_id)
        if not user.employee_ids:
            raise UserError(
                _('User %s is not linked to an employee') % user.name
            )
        else:
            employee = user.employee_ids[0]

        # Get firstname and lastname from name
        name = employee.name.split(" ", 1)
        if len(name) > 1:
            name = [" ".join(name[1:]), name[0]]
        else:
            while len(name) < 2:
                name.append('')
        firstname = name[1]
        lastname = name[0]

        # Combine all e-mails to a list
        emails = []
        if employee.work_email:
            emails.append(employee.work_email)
        if employee.other_work_emails:
            for email in employee.other_work_emails.split('\n'):
                if email not in emails:
                    emails.append(email)

        # Combine all websites to a list
        websites = []
        if employee.address_id.website:
            websites.append(employee.address_id.website)
        if employee.other_websites:
            for website in employee.other_websites.split('\n'):
                if website not in websites:
                    websites.append(website)

        job_title = employee.job_title or ''
        phone = employee.mobile_phone or ''
        phone_ext = employee.work_phone_extension or ''
        street1 = employee.address_id.street or ''
        street2 = employee.address_id.street2 or ''
        city = employee.address_id.city or ''
        zip = employee.address_id.zip or ''
        company_name = employee.address_id.name or ''
        company_phone = employee.address_id.phone or ''
        company_fax = employee.address_id.fax or ''

        def replace_space_thinspace(value):
            """ Replace standard space with thinspace
            """
            return value.replace(' ', ' ')

        variables = {
            'user': user,
            'employee': employee,
            'firstname': firstname,
            'lastname': lastname,
            'job_title': job_title,
            'emails': emails,
            'phone': replace_space_thinspace(phone),
            'phone_ext': phone_ext,
            'street1': street1,
            'street2': street2,
            'city': city,
            'zip': zip,
            'company_name': company_name,
            'company_phone': replace_space_thinspace(company_phone),
            'company_fax': replace_space_thinspace(company_fax),
            'websites': websites,
            'ctx': self._context,  # context kw would clash with mako internals
        }

        try:
            render_result = template.render(variables)
        except Exception as e:
            _logger.info(
                "Failed to render template %r using values %r" %
                (template, variables),
                exc_info=True
            )
            raise UserError(
                _("Failed to render template %r using values %r") %
                (template, variables) + "\n\n%s: %s" %
                (type(e).__name__, str(e))
            )
        return render_result

