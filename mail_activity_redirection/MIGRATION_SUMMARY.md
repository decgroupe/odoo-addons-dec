# Migration summary: `mail_activity_redirection` 14.0 to 18.0

## Step 0 - Feature check (~1 min)

No overlap found in Odoo 18.0 core or OCA.

## Pre-Step 6x - DB init (~1 min, background)

Database `demo18_mail_activity_redirection` created with base module.

## Step 1 - Migration tool (~2 min)

`sk-migrate` bumped version to `18.0.1.0.0`, set `installable: True`, ran initial
pre-commit.

## Step 2 - Manifest (~0 min)

Already correct (`license` present, `installable: True`).

## Step 3 - Pre-commit formatting (~2 min)

Fixed deprecated `<data>` node to `<odoo noupdate="1">`, removed executable bit from
CSV, pre-commit passes for module files.

## Step 4 - Code-level changes (~5 min)

- `mail_activity_mixin.py`: replaced `from odoo import _, models` with
  `from odoo import models`; replaced `_("...") % (...)` with
  `self.env._("... %(user)s ... %(rule)s", user=..., rule=...)`
- `views/mail_activity_redirection.xml`: renamed view from `...tree@...` to
  `...list@...`; converted `attrs="{'invisible': [('active', '=', True)]}"` to
  `invisible="active"`
- `views/res_config_settings.xml`: updated `inherit_id` to
  `mail.res_config_settings_view_form`, changed XPath to `//block[@id='emails']`,
  rewrote content to use new `<setting>` format
- Added docstrings to all functions missing them in `mail_activity_redirection.py`

## Step 5 - Tests (~5 min)

Created `tests/__init__.py`, `tests/common.py`,
`tests/test_mail_activity_redirection.py` with 17 test cases covering `match()`,
`activity_schedule()` redirection, `_link_to_mail_activity_redirection()` history
capping, default sequence, and view field presence.

## Step 6a - Test run (~3 min)

All 17 tests passed.

Coverage:

| File                                  | Stmts | Miss | Coverage  |
| ------------------------------------- | ----- | ---- | --------- |
| `models/mail_activity.py`             | 13    | 0    | 100%      |
| `models/mail_activity_mixin.py`       | 27    | 5    | 81.5%     |
| `models/mail_activity_redirection.py` | 69    | 6    | 91.3%     |
| **Package overall**                   |       |      | **90.2%** |

## Step 7a - Description (~2 min)

Rewrote `readme/DESCRIPTION.md` with user-facing section and technical details;
regenerated `README.rst`.

## Step 7b - Final pre-commit (~2 min)

All hooks pass for `mail_activity_redirection`. Only pre-existing `ruff` failures in
unrelated `res_users_signature` module remain.

**Total elapsed: ~24 min**
