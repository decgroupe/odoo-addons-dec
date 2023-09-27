# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

import io
import string
import unicodedata
import uuid

import psycopg2
import psycopg2.extensions

from odoo import fields, models

MODENAME = "xml_export"


SEPARATOR = "_"
SAFE_CHARS = string.ascii_letters + string.digits + SEPARATOR


def unaccent(txt):
    nfkd_form = unicodedata.normalize("NFKD", txt)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class BaseModel(models.BaseModel):
    _inherit = "base"

    xid = fields.Char(
        string="XML-ID",
        compute="_compute_xid",
        inverse="_inverse_xid",
        help="ID of the record defined in xml file",
    )

    def _compute_xid(self):
        """Also note that `ir.model.data` owns two methods `xmlid_to_object` and
        `xmlid_to_res_id` to retrieve this data
        """
        xml_ids, model_datas = (
            self.env["ir.model.data"].sudo().res_id_to_xmlid(self._name, self.ids)
        )
        for rec in self:
            rec.xid = xml_ids.get(rec.id, [""])[0]

    def _inverse_xid(self):
        IrModelData = self.env["ir.model.data"].sudo()
        xml_ids, model_datas = IrModelData.res_id_to_xmlid(self._name, self.ids)
        for rec in self:
            model_data_ids = model_datas.get(rec.id, [])
            if not rec.xid:
                if model_data_ids:
                    IrModelData.browse(model_data_ids).unlink()
                continue
            module, name = rec.xid.split(".", 1)
            model_data = IrModelData.search(
                [("module", "=", module), ("name", "=", name)]
            )
            if not model_data and model_data_ids:
                model_data = IrModelData.browse(model_data_ids[0])
            if model_data:
                model_data.write(
                    {
                        "module": module,
                        "name": name,
                        "model": rec._name,
                        "res_id": rec.id,
                    }
                )
                # Manually add this XML-ID to the list of loaded data, otherwise it will
                # be deleted in `_process_end`
                self.pool.loaded_xmlids.add(rec.xid)

    def _get_xml_record_human_name(self):
        self.ensure_one()
        record_name = self[self._rec_name] or ""
        return self._compose_xml_record_human_name(self.id, record_name)

    def _compose_xml_record_human_name(self, res_id=False, record_name=""):
        try:
            record_name = unaccent(record_name)
            record_name = record_name.lower()
            record_name = record_name.replace(" ", SEPARATOR).replace("-", SEPARATOR)
            name = list(
                filter(lambda x: x in SAFE_CHARS, unaccent(record_name).lower())
            )
            name = "".join(name)
        except:
            name = ""
        if name and res_id:
            name = "%d%s%s" % (res_id, SEPARATOR * 2, name)
        else:
            # Fallback to default Odoo naming implementation
            name = SEPARATOR + uuid.uuid4().hex[:8]
        return "%s_%s" % (self._table, name)

    def ensure_human_xml_id(self, skip=False):
        """Improved version of `__ensure_xml_id` from `./odoo/odoo/models.py`
        Create missing external ids for records in ``self``, and return an
        iterator of pairs ``(record, xmlid)`` for the records in ``self``.

        :rtype: Iterable[Model, str | None]
        """
        if skip:
            return ((record, None) for record in self)

        if not self:
            return iter([])

        if not self._is_an_ordinary_table():
            raise Exception(
                "You can not export the column ID of model %s, because the "
                "table %s is not an ordinary table." % (self._name, self._table)
            )

        cr = self.env.cr
        cr.execute(
            """
            SELECT res_id, module, name
            FROM ir_model_data
            WHERE model = %s AND res_id in %s
            """,
            (self._name, tuple(self.ids)),
        )
        xids = {res_id: (module, name) for res_id, module, name in cr.fetchall()}

        def to_xid(record_id):
            (module, name) = xids[record_id]
            return ("%s.%s" % (module, name)) if module else name

        # create missing xml ids
        missing = self.filtered(lambda r: r.id not in xids)
        if missing:
            xids.update(
                (r.id, (MODENAME, r._get_xml_record_human_name())) for r in missing
            )
            fields = ["module", "model", "name", "res_id"]

            # disable eventual async callback / support for the extent of
            # the COPY FROM, as these are apparently incompatible
            callback = psycopg2.extensions.get_wait_callback()
            psycopg2.extensions.set_wait_callback(None)
            try:
                cr.copy_from(
                    io.StringIO(
                        "\n".join(
                            "%s\t%s\t%s\t%d"
                            % (
                                MODENAME,
                                record._name,
                                xids[record.id][1],
                                record.id,
                            )
                            for record in missing
                        )
                    ),
                    table="ir_model_data",
                    columns=fields,
                )
            finally:
                psycopg2.extensions.set_wait_callback(callback)
            self.env["ir.model.data"].invalidate_cache(fnames=fields)

        return ((record, to_xid(record.id)) for record in self)
