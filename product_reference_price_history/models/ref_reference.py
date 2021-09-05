# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import time
import logging

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from werkzeug import url_encode

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)


class RefReference(models.Model):
    _inherit = 'ref.reference'

    price_ids = fields.One2many(
        'ref.price',
        'reference_id',
        string='Prices',
        oldname='price_lines',
    )

    @api.multi
    def run_material_cost_scheduler(self):
        MrpBom = self.env['mrp.bom']
        RefPrice = self.env['ref.price']

        # Get current day/time as seen by the user (timezone)
        start_time = fields.Datetime.context_timestamp(self, datetime.now())

        if not self.ids:
            references = self.search([])
        else:
            references = self

        new_prices = RefPrice
        for reference in references:
            if reference.category_id.code in ['ADT']:
                continue
            cost_price = 0.0
            product_count = 0
            if reference.product_id and reference.product_id.bom_ids:
                bom_id = MrpBom._bom_find(product_tmpl=reference.product_id)
                if bom_id:
                    _logger.info(
                        'Compute material cost price for [%s] %s',
                        reference.value, reference.product_id.name
                    )
                    try:
                        cost_price = bom_id.cost_price
                        product_count = len(bom_id.bom_line_ids)
                    except Exception as e:
                        _logger.exception(
                            "Failed to get cost price for [%s] %s\n %s",
                            reference.value, reference.product_id.name, e
                        )

            ref_price = False
            ref_prices = RefPrice.search(
                [('reference_id', '=', reference.id)], limit=1
            )
            if ref_prices:
                ref_price = ref_prices[0]

            if not ref_price or (
                round(ref_price.value, 2) != round(cost_price, 2)
            ):
                data = {
                    'reference_id': reference.id,
                    'value': cost_price,
                    'product_count': product_count,
                }
                new_price = RefPrice.create(data)
                new_prices += new_price
                _logger.info(
                    'New price stored for [%s] %s', reference.value,
                    reference.product_id.name
                )
            else:
                _logger.info(
                    'Price did not change for [%s] %s', reference.value,
                    reference.product_id.name
                )

            # if len(new_prices) >= 5:
            #     break

        end_time = fields.Datetime.context_timestamp(self, datetime.now())

        # https://stackoverflow.com/questions/538666/format-timedelta-to-string
        total_seconds = (end_time - start_time).total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = '{:02}:{:02}:{:02}'.format(
            int(hours), int(minutes), int(seconds)
        )

        ctx = self.env.context.copy()
        ctx.update(
            {
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration,
            }
        )

        references.with_context(ctx).generate_material_cost_report()

    @api.multi
    def generate_material_cost_report(self, date_ref1=False, date_ref2=False):
        RefPrice = self.env['ref.price']

        # Get current day as seen by the user (timezone)
        today = fields.Date.context_today(self)

        report_lines = []

        if not self.ids:
            references = self.search([])
        else:
            references = self

        total_references = 0
        total_products = 0
        for reference in references:
            if reference.category_id.name in ['ADT']:
                continue

            def get_prices_before(reference, date_ref):
                return RefPrice.search(
                    [
                        ('reference_id', '=', reference.id),
                        ('date', '<=', date_ref)
                    ],
                    limit=1
                )

            ref1_ids = RefPrice
            ref2_ids = RefPrice
            if date_ref1:
                ref1_ids = get_prices_before(reference, date_ref1)
            if date_ref2:
                ref1_ids = get_prices_before(reference, date_ref2)

            if ref1_ids and ref2_ids:
                prices = ref2_ids + ref1_ids
            else:
                prices = RefPrice.search(
                    [('reference_id', '=', reference.id)], limit=2
                )

            if len(prices) >= 2:
                if round(prices[0].value, 2) > round(prices[1].value, 2) and (
                    # IF two dates were given to compute price diff
                    (date_ref1 and date_ref2) or
                    # OR the last price diff was computed in the last 24
                    # hours
                    (prices[0].date >= today - relativedelta(days=1)) or
                    # OR forced by context
                    self.env.context.get('ignore_date')
                ):
                    line = self._get_reference_report_line(reference, prices)
                    report_lines.append(line)
                    total_references += 1
                    total_products += line.get('price0_product_count', 0)
                    _logger.info(
                        '[{}] {} added for reporting'.format(
                            reference.value, reference.product_id.name
                        )
                    )
                    # if len(report_lines) > 10:
                    #     break

        # We create a copy of the context that will be used to
        # render the report
        ctx = self.env.context.copy()
        ctx.update(
            {
                'today': today,
                'total_references': total_references,
                'total_products': total_products,
            }
        )

        if report_lines:
            self.with_context(ctx)._send_report(report_lines)

    def _get_reference_report_line(self, reference, prices):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ref_action = self.env.ref('product_reference.act_window_ref_reference')
        href = '%s/web#%s' % (
            base,
            url_encode(
                {
                    'id': reference.id,
                    'model': 'ref.reference',
                    'action': ref_action.id,
                    'view_type': 'form',
                }
            )
        )

        def formatted_price(value):
            return formatLang(
                self.env,
                value,
                currency_obj=reference.product_id.currency_id,
                digits=2
            )

        raw_diff = prices[0].value - prices[1].value
        return {
            'id': reference.id,
            'reference': reference,
            'href': href,
            'price0_date': prices[0].date,
            'price0_fmt': formatted_price(prices[0].value),
            'price0_product_count': prices[0].product_count or 0,
            'price1_date': prices[1].date,
            'price1_fmt': formatted_price(prices[1].value),
            'price1_product_count': prices[1].product_count or 0,
            'diff': formatted_price(raw_diff),
            'raw_diff': raw_diff,
        }

    def _send_report(self, report_lines):
        # Sort by diff
        report_lines = sorted(
            report_lines,
            key=lambda k: k['raw_diff'],
            reverse=True,
        )

        # We create a copy of the context that will be used to
        # render the report
        ctx = self.env.context.copy()
        ctx.update(
            {
                'company_name': self.env.user.company_id.name,
                'dbname': self.env.cr.dbname,
                'report_lines': report_lines,
            }
        )

        # Get Jinja2 template
        email_template = self.env.ref(
            'product_reference_price_history.material_cost_report_email_template'
        )
        # Override some values
        values = {
            'email_to':
                ','.join(['decindustrie@gmail.com', self.env.user.email]),
            'email_from':
                self.env.user.company_id.email,
            'author_id':
                self.env.user.partner_id.id,
        }
        # Render the e-mail using given context
        email_template.sudo().with_context(ctx).send_mail(
            False, force_send=True, email_values=values
        )
        # Note that we could set force_send to False in order to
        # edit email body before sending it using the id returned by
        # send_mail()
