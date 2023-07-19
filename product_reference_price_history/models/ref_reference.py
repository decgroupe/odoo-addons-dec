# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from werkzeug import url_encode

from odoo import api, fields, models
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)


class RefReference(models.Model):
    _inherit = "ref.reference"

    price_ids = fields.One2many(
        comodel_name="ref.price",
        inverse_name="reference_id",
        string="Prices",
    )

    def run_material_cost_scheduler(self):
        if not self.ids:
            domain = []
            references = self.search(domain)
        else:
            references = self

        references._run_material_cost_scheduler()

    def _run_material_cost_scheduler(self):
        MrpBom = self.env["mrp.bom"]
        RefPrice = self.env["ref.price"]

        # Get current day/time as seen by the user (timezone)
        start_time = fields.Datetime.context_timestamp(self, datetime.now())

        new_prices = RefPrice
        for rec in self:
            if rec.category_id.code in ["ADT"]:
                continue
            cost_price = 0.0
            product_count = 0
            if rec.product_id and rec.product_id.bom_ids:
                bom_id = MrpBom._bom_find(product_tmpl=rec.product_id)
                if bom_id:
                    _logger.info(
                        "Compute material cost price for [%s] %s",
                        rec.value,
                        rec.product_id.name,
                    )
                    try:
                        cost_price = bom_id.cost_price
                        product_count = len(bom_id.bom_line_ids)
                    except Exception as e:
                        _logger.exception(
                            "Failed to get cost price for [%s] %s\n %s",
                            rec.value,
                            rec.product_id.name,
                            e,
                        )

            ref_price = False
            ref_prices = RefPrice.search([("reference_id", "=", rec.id)], limit=1)
            if ref_prices:
                ref_price = ref_prices[0]

            if not ref_price or (round(ref_price.value, 2) != round(cost_price, 2)):
                data = {
                    "reference_id": rec.id,
                    "value": cost_price,
                    "product_count": product_count,
                }
                new_price = RefPrice.create(data)
                new_prices += new_price
                _logger.info(
                    "New price stored for [%s] %s", rec.value, rec.product_id.name
                )
            else:
                _logger.info(
                    "Price did not change for [%s] %s", rec.value, rec.product_id.name
                )

            # if len(new_prices) >= 5:
            #     break

        end_time = fields.Datetime.context_timestamp(self, datetime.now())

        # https://stackoverflow.com/questions/538666/format-timedelta-to-string
        total_seconds = (end_time - start_time).total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

        ctx = self.env.context.copy()
        ctx.update(
            {
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
            }
        )

        self.with_context(ctx).generate_material_cost_report()

    def generate_material_cost_report(
        self,
        date_before=False,
        date_after=False,
        format_prices=True,
        email_to=False,
    ):
        if not self.ids:
            domain = [("state", "!=", "obsolete")]
            references = self.search(domain)
        else:
            references = self

        references._generate_material_cost_report(
            date_before, date_after, format_prices, email_to
        )

    def _get_price_from_range(self, date_before=False, date_after=False):
        self.ensure_one()
        domain = [("reference_id", "=", self.id)]
        if date_before:
            domain.append(("date", "<=", date_before))
        if date_after:
            domain.append(("date", ">=", date_after))
        return self.env["ref.price"].search(domain, limit=1)

    def _get_last_prices(self):
        self.ensure_one()
        domain = [("reference_id", "=", self.id)]
        return self.env["ref.price"].search(domain, limit=2)

    def _generate_material_cost_report(
        self, date_before, date_after, format_prices, email_to
    ):
        # Get current day as seen by the user (timezone)
        today = fields.Date.context_today(self)

        report_lines = []
        total_references = 0
        total_products = 0
        for rec in self:
            if rec.category_id.code in ["ADT"]:
                continue

            if date_before and date_after:
                price1_id = rec._get_price_from_range(date_before, date_after)
                # When a date is set then we must have a valid price
                if not price1_id:
                    continue
                price2_id = rec._get_price_from_range(date_before=date_after)
                # When a date is set then we must have a valid price
                if not price2_id:
                    continue
                prices = price1_id + price2_id
            else:
                prices = rec._get_last_prices()

            if len(prices) >= 2:
                if round(prices[0].value, 2) > round(prices[1].value, 2) and (
                    # IF two dates were given to compute price diff
                    (date_before and date_after)
                    or
                    # OR the last price diff was computed in the last 24
                    # hours
                    (prices[0].date >= today - relativedelta(days=1))
                    or
                    # OR forced by context
                    self.env.context.get("ignore_date")
                ):
                    line = self._get_reference_report_line(rec, prices, format_prices)
                    report_lines.append(line)
                    total_references += 1
                    total_products += line.get("price0_product_count", 0)
                    _logger.info(
                        "[{}] {} added for reporting".format(
                            rec.value, rec.product_id.name
                        )
                    )
                    # if len(report_lines) > 10:
                    #     break

        # We create a copy of the context that will be used to
        # render the report
        ctx = self.env.context.copy()
        ctx.update(
            {
                "today": today,
                "total_references": total_references,
                "total_products": total_products,
            }
        )

        if report_lines:
            self.with_context(ctx)._send_report(report_lines, email_to)

    def _get_reference_report_line(self, reference, prices, format_prices):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        ref_action = self.env.ref("product_reference.act_window_ref_reference")
        href = "%s/web#%s" % (
            base,
            url_encode(
                {
                    "id": reference.id,
                    "model": "ref.reference",
                    "action": ref_action.id,
                    "view_type": "form",
                }
            ),
        )

        def formatted_price(value):
            if format_prices:
                return formatLang(
                    self.env,
                    value,
                    currency_obj=reference.product_id.currency_id,
                    digits=2,
                )
            else:
                return round(value, 2)

        raw_diff = prices[0].value - prices[1].value
        if prices[0].value and (prices[1].value != 0):
            diff_percent = (prices[0].value - prices[1].value) * 100 / prices[1].value
        else:
            diff_percent = 0

        return {
            "id": reference.id,
            "reference": reference,
            "href": href,
            "price0_date": prices[0].date,
            "price0_fmt": formatted_price(prices[0].value),
            "price0_product_count": prices[0].product_count or 0,
            "price1_date": prices[1].date,
            "price1_fmt": formatted_price(prices[1].value),
            "price1_product_count": prices[1].product_count or 0,
            "diff": formatted_price(raw_diff),
            "diff_percent": round(diff_percent),
            "raw_diff": raw_diff,
        }

    @api.model
    def _get_cost_report_default_email(self):
        email = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("product_reference_price_history.cost_report_email", "")
        )
        return email

    def _send_report(self, report_lines, email_to=False):
        # Sort by diff
        report_lines = sorted(
            report_lines,
            key=lambda k: k["diff_percent"],
            reverse=True,
        )
        # We create a copy of the context that will be used to
        # render the report
        ctx = self.env.context.copy()
        ctx.update(
            {
                "company_name": self.env.user.company_id.name,
                "dbname": self.env.cr.dbname,
                "report_lines": report_lines,
            }
        )
        # Get Jinja2 template
        email_template = self.env.ref(
            "product_reference_price_history.material_cost_report_email_template"
        )
        # Set default emails if not set
        if not email_to:
            email_to = ",".join(
                [self._get_cost_report_default_email(), self.env.user.email]
            )
        # Override some values
        values = {
            "email_to": email_to,
            "email_from": self.env.user.company_id.email,
            "author_id": self.env.user.partner_id.id,
        }
        # Render the e-mail using given context
        email_template.sudo().with_context(ctx).send_mail(
            False, force_send=True, email_values=values
        )
        # Note that we could set `force_send` to False in order to
        # edit email body before sending it using the id returned by
        # `send_mail()`
