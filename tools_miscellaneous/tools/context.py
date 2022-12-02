# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo.tools.safe_eval import safe_eval

DUMMY_ACTIVE_ID = "#ACTIVE_ID"


def safe_eval_action_context_string_to_dict(action):
    return safe_eval_active_context_string_to_dict(action.get('context', '{}'))


def safe_eval_active_context_string_to_dict(context):
    locals_dict = {
        'active_id': DUMMY_ACTIVE_ID,
    }
    try:
        ctx_as_dict = safe_eval(
            context,
            locals_dict=locals_dict,
        )
    except:
        ctx_as_dict = {}
    return ctx_as_dict


def safe_eval_active_context_dict_to_string(context):
    ctx_as_string = str(context).replace(
        "'{0}'".format(DUMMY_ACTIVE_ID),
        "active_id",
    )
    return ctx_as_string
