from . import bench
from . import html_helper
from . import console_helper
from . import context

# import the real Gettext shortcut
from odoo import _ as _t


def _(value):
    """Fake Gettext underscore shortcuts to force Odoo generating a translation entry"""
    return value


def update_translation(env, xmlid, vals):
    # force translation update
    rec = env.ref(xmlid)
    for lang in env["res.lang"].get_installed():
        # the Gettext alias `_` will use `inspect.currentframe` to retrieve references
        # on `context` and `cr`, that's why we are faking them here
        context = {"lang": lang[0]}
        cr = env.cr
        # ready to update translation
        rec_with_lang = rec.with_context(**context)
        trans_vals = {}
        for field, value in vals.items():
            # get the translated value
            trans_vals[field] = _t(value)
        # write translations
        rec_with_lang.write(trans_vals)
