# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

_logger = logging.getLogger(__name__)

MODULE = 'hr_expense_easy'


def get_account(env, code):
    Account = env['account.account']
    account = Account.search([('code', '=', code)], limit=1)
    if not account:
        _logger.warning('Code %s not found', code)
    return account


def assign_category_account(env, ref, code):
    account = get_account(env, code)
    category_id = env.ref(MODULE + '.cat_' + ref)
    category_id.property_account_expense_categ_id = account


def assign_product_account(env, ref, code):
    account = get_account(env, code)
    product_id = env.ref(MODULE + '.product_product_expense_' + ref)
    product_id.property_account_expense_id = account


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    assign_category_account(env, 'transport', '625100')
    assign_category_account(env, 'catering', '625600')
    assign_category_account(env, 'lodging', '625100')
    assign_category_account(env, 'other', '472000')

    assign_product_account(env, 'plane', '625100')
    assign_product_account(env, 'bus', '625100')
    assign_product_account(env, 'fuel', '606800')
    assign_product_account(env, 'car_rent', '613500')
    assign_product_account(env, 'car_metro', '625100')
    assign_product_account(env, 'car_park', '625100')
    assign_product_account(env, 'toll', '625100')
    assign_product_account(env, 'taxi', '625100')
    assign_product_account(env, 'train', '625100')

    assign_product_account(env, 'consumption', '625600')
    assign_product_account(env, 'restaurant', '625600')
    assign_product_account(env, 'food', '625600')

    assign_product_account(env, 'hotel', '625100')

    assign_product_account(env, 'infraction', '637800')
    assign_product_account(env, 'vehicle_insurance', '616300')
    assign_product_account(env, 'other_insurance', '616100')
    assign_product_account(env, 'customer_gifts', '623400')
    assign_product_account(env, 'membership_fee', '628100')
    assign_product_account(env, 'decoration', '623800')
    assign_product_account(env, 'various', '472000')
    assign_product_account(env, 'documentation_book', '618100')
    assign_product_account(env, 'maintenance_repair_equipment', '615500')
    assign_product_account(env, 'maintenance_repair_vehicle', '615500')
    assign_product_account(env, 'exhibition_fair', '623300')
    assign_product_account(env, 'training', '631300')
    assign_product_account(env, 'administrative_supplies', '606400')
    assign_product_account(env, 'postal_charges', '626100')
    assign_product_account(env, 'newspapers', '618100')
    assign_product_account(env, 'equipment_rental', '613500')
    assign_product_account(env, 'room_rental', '613200')
    assign_product_account(env, 'small_equipment', '606300')
    assign_product_account(env, 'pharmacy', '647500')
    assign_product_account(env, 'tips_usual_donations', '623800')
    assign_product_account(env, 'foodstuffs', '625700')
    assign_product_account(env, 'maintenance_products', '606300')
    assign_product_account(env, 'advertising', '623100')
    assign_product_account(env, 'publication_and_print', '623700')
    assign_product_account(env, 'seminars_colloquiums_conferences', '618500')
    assign_product_account(env, 'phone', '626200')
    assign_product_account(env, 'carrier', '624100')
    assign_product_account(env, 'work_clothes', '606300')
    assign_product_account(env, 'internet', '626200')
