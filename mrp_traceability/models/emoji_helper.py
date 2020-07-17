# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2020

# ⭕

def production_state_to_emoji(state):
    res = state
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

def purchase_state_to_emoji(state):
    res = state
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

def stockmove_state_to_emoji(state):
    res = state
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
