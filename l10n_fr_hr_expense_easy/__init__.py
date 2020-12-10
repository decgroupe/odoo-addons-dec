# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

import logging

_logger = logging.getLogger(__name__)

MODULE = 'hr_expense_easy'


def post_init(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    Account = env['account.account']

    def assign_category_account(ref, code):
        account = Account.search([('code', '=', code)], limit=1)
        if not account:
            _logger.warning('Code %s not found', code)
        env.ref(
            MODULE + '.cat_' + ref
        ).property_account_expense_categ_id = account

    assign_category_account('transport', '625100')
    assign_category_account('catering', '625600')
    assign_category_account('lodging', '625100')
    assign_category_account('other', '472000')

    def assign_product_account(ref, code):
        account = Account.search([('code', '=', code)], limit=1)
        if not account:
            _logger.warning('Code %s not found', code)
        env.ref(
            MODULE + '.product_product_expense_' + ref
        ).property_account_expense_id = account

    assign_product_account('plane', '625100')
    assign_product_account('bus', '625100')
    assign_product_account('fuel', '606800')
    assign_product_account('car_rent', '613500')
    assign_product_account('car_metro', '625100')
    assign_product_account('car_park', '625100')
    assign_product_account('toll', '625100')
    assign_product_account('taxi', '625100')
    assign_product_account('train', '625100')

    assign_product_account('consumption', '625600')
    assign_product_account('restaurant', '625600')
    assign_product_account('food', '625600')

    assign_product_account('hotel', '625100')

    assign_product_account('infraction', '637800')
    assign_product_account('vehicle_insurance', '616300')
    assign_product_account('other_insurance', '616100')
    assign_product_account('customer_gifts', '623400')
    assign_product_account('membership_fee', '628100')
    assign_product_account('decoration', '623800')
    assign_product_account('various', '472000')
    assign_product_account('documentation_book', '618100')
    assign_product_account('maintenance_repair_equipment', '615500')
    assign_product_account('maintenance_repair_vehicle', '615500')
    assign_product_account('exhibition_fair', '623300')
    assign_product_account('training', '631300')
    assign_product_account('administrative_supplies', '606400')
    assign_product_account('postal_charges', '626100')
    assign_product_account('newspapers', '618100')
    assign_product_account('equipment_rental', '613500')
    assign_product_account('room_rental', '613200')
    assign_product_account('small_equipment', '606300')
    assign_product_account('pharmacy', '647500')
    assign_product_account('tips_usual_donations', '623800')
    assign_product_account('foodstuffs', '625700')
    assign_product_account('maintenance_products', '606300')
    assign_product_account('advertising', '623100')
    assign_product_account('publication_and_print', '623700')
    assign_product_account('seminars_colloquiums_conferences', '618500')
    assign_product_account('phone', '626200')
    assign_product_account('carrier', '624100')
    assign_product_account('work_clothes', '606300')
    assign_product_account('internet', '626200')
