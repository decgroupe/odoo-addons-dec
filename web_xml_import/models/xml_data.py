# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

import logging
import os.path
import subprocess

from lxml import etree

from odoo import fields, models
from odoo.tools import config
from odoo.tools.convert import xml_import

try:
    import jingtrang
except ImportError:
    jingtrang = None

_logger = logging.getLogger(__name__)


class XmlData(models.Model):
    _name = "xml.data"

    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide this data without removing it.",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    note = fields.Text(
        string="Description",
    )
    module = fields.Char(
        string="Module",
        default="xml_import",
        required=True,
    )
    content = fields.Text(
        string="Data",
    )

    def action_import_init(self):
        for rec in self:
            rec._import(mode="init")

    def action_import_update(self):
        for rec in self:
            rec._import(mode="update")

    def _check_xmldoc(self, doc, name):
        schema = os.path.join(config["root_path"], "import_xml.rng")
        relaxng = etree.RelaxNG(etree.parse(schema))
        try:
            relaxng.assert_(doc)
        except Exception:
            _logger.exception(
                "The XML file '%s' does not fit the required schema !", name
            )
            args = ["pyjing", schema, name]
            if jingtrang:
                try:
                    p = subprocess.run(args, stdout=subprocess.PIPE)
                    _logger.warning(p.stdout.decode())
                except Exception:
                    _logger.warn("Run manually:\n%s", " ".join(args))
            else:
                for e in relaxng.error_log:
                    _logger.warning(e)
                _logger.info(
                    "Install 'jingtrang' for more precise and useful validation messages."
                )
                _logger.warn("Or run manually if needed:\n%s", " ".join(args))
            raise

    def _import(self, mode="init"):
        """This code is partially the same that `convert_xml_import` from
        `odoo.tools.convert`, excepts that data is loaded from a string instead of
        a file
        """
        self.ensure_one()
        doc = etree.fromstring(self.content.encode("utf-8"))
        self._check_xmldoc(doc, self.name)
        obj = xml_import(
            self.env.cr,
            module=self.module,
            idref=None,
            mode=mode,
            noupdate=False,
            xml_filename=self.name,
        )
        obj.parse(doc)
