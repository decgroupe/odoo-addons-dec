# Copyright (C) 2014 Sudokeys (<http://www.sudokeys.com>)
# Copyright (C) 2017 Komit (<http://www.komit-consulting.com>)
#
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Web Widget Text Markdown",
    "version": "12.0.1.0.0",
    "author": "Alexandre Díaz, "
    "Komit, "
    "Sudokeys, "
    "Sunflower IT, "
    "Odoo Community Association (OCA)",
    "category": "Web",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/web",
    "summary": "Widget to text fields that adds markdown support",
    "depends": ["web"],
    "demo": ["demo/bootstrap_markdown.xml"],
    "data": ["views/assets.xml"],
    "qweb": ["static/src/xml/bootstrap_markdown.xml"],
    "installable": True,
    "auto_install": False,
    "application": False,
}

# https://github.com/showdownjs/showdown
# Extension list: https://github.com/showdownjs/showdown/wiki

# Extensions:
# - https://github.com/showdownjs/table-extension (deprecated)
# - https://github.com/ravisorg/showdown-toc
# - https://github.com/halbgut/showdown-footnotes