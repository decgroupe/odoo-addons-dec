# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Apr 2020

# ⭕

def production_to_emoji(production):
    res = production.state
    if res == 'confirmed':
        res = '🏳️'
    elif res == 'planned':
        res = '📅'
    elif res == 'progress':
        res = '🚧'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res

def purchase_to_emoji(purchase):
    res = purchase.state
    if res == 'draft':
        res = '🏳️'
    elif res == 'sent':
        res = '📩'
    elif res == 'to approve':
        res = '⏳'
    elif res == 'purchase':
        res = '💲'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res

def stockmove_to_emoji(move):
    res = move.state
    if res == 'draft':
        res = '🏳️'
    elif res == 'waiting':
        res = '⛓️'
    elif res == 'confirmed':
        res = '⏳'
    elif res == 'partially_available':
        res = '✴️'
    elif res == 'assigned':
        res = '✳️'
    elif res == 'done':
        res = '✅'
    elif res == 'cancel':
        res = '❌'
    return res

def product_type_to_emoji(product_type):
    res = product_type
    if res == 'product':
        res = '➕'
    elif res == 'consu':
        res = '🧃'
    elif res == 'service':
        res = '🛎️'
    return res
