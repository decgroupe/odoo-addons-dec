# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

import logging
from xml.dom import minidom

from odoo.models import MAGIC_COLUMNS, fix_import_export_id_paths

_logger = logging.getLogger(__name__)

INDENT = "    "


class ExportXmlWriter:
    xmlid_cache = {}

    _context = property(lambda self: self.env.context)

    def __init__(self, env):
        self.env = env

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def with_context(self, *args, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        context = dict(args[0] if args else self._context, **kwargs)
        self.env = self.env(context=context)
        return self

    def _get_or_create_xmlid(self, model_name, data, res_id=False, import_compat=False):
        """Get or create the XML-id for a given model and res_id from `ir.model.data` or
        create a new one (human readable) if not found."""
        xml_id = False
        if res_id:
            if import_compat:
                self.env[model_name].browse(res_id)._ensure_human_xml_id()
            xml_id = self._get_xmlid(model_name, res_id)
            if not xml_id:
                xml_id = self.env[model_name]._compose_xml_record_human_name(
                    res_id, data.get("name", "")
                )
        return xml_id

    def _get_xmlid(self, model_name, res_id):
        """Get the XML-id for a given model and res_id from `ir.model.data` or from
        xmlid_cache if already fetched.

        Returns:
            str: xml_id
        """
        xml_id = False
        if (model_name, res_id) in self.xmlid_cache:
            xml_id = self.xmlid_cache[(model_name, res_id)]
        else:
            IrModelData = self.env["ir.model.data"]
            domain = [("model", "=", model_name), ("res_id", "=", res_id)]
            model_data = IrModelData.search(domain, limit=1)
            if model_data:
                xml_id = model_data.module + "." + model_data.name
        return xml_id

    def _get_fields_to_bypass(self):
        DEFAULT_FIELDS = [
            "display_name",
            "__last_update",
        ]
        return MAGIC_COLUMNS + DEFAULT_FIELDS

    def _create_record(self, doc, model_name, data, record_xml_id):  # noqa: C901
        Model = self.env[model_name]
        record = doc.createElement("record")
        record.setAttribute("model", model_name)
        record.setAttribute("id", record_xml_id)
        record_list = []
        fields = Model.fields_get()
        for key, val in data.items():
            if key in self._get_fields_to_bypass():
                continue
            # functional fields check
            if (
                key in Model._fields.keys()
                and not Model._fields[key].store
                and not Model._fields[key].inverse
            ):
                continue
            if not (val or (fields[key]["type"] == "boolean")):
                continue
            if (
                fields[key]["type"] in ("integer", "float")
                or fields[key]["type"] == "selection"
                and isinstance(val, int)
            ):
                field = doc.createElement("field")
                field.setAttribute("name", key)
                field.setAttribute("eval", val and str(val) or "False")
                record.appendChild(field)
            elif fields[key]["type"] in ("boolean",):
                field = doc.createElement("field")
                field.setAttribute("name", key)
                field.setAttribute("eval", val and "True" or "False")
                record.appendChild(field)
            elif fields[key]["type"] in ("many2one",):
                sub_model_name = fields[key]["relation"]
                field = doc.createElement("field")
                field.setAttribute("name", key)
                if type(val) in (str, str):
                    xml_id = val
                else:
                    xml_id = self._get_xmlid(sub_model_name, val)
                if not xml_id:
                    SubModel = self.env[sub_model_name]
                    field.setAttribute("model", sub_model_name)
                    # Ensure this model is namable
                    if SubModel._rec_name:
                        fld_nm = SubModel._rec_name
                        val = SubModel.browse(val)
                        name = val.read([fld_nm])[0][fld_nm] or False
                        field.setAttribute("search", str([(str(fld_nm), "=", name)]))
                else:
                    field.setAttribute("ref", xml_id)
                record.appendChild(field)
            elif fields[key]["type"] in ("one2many",):
                sub_model_name = fields[key]["relation"]
                xml_ids = []
                for valitem in val or []:
                    if (
                        valitem[0] in (0, 1)
                        and valitem[2].get("name") not in self._get_fields_to_bypass()
                    ):
                        if valitem[0] == 0:
                            res_id = valitem[2].get("id")
                            xml_id = self._get_or_create_xmlid(
                                sub_model_name, valitem[2], res_id
                            )
                            valitem[1] = xml_id
                        else:
                            res_id = valitem[1]
                            xml_id = self._get_xmlid(sub_model_name, res_id)
                            if not xml_id:
                                xml_id = self._get_or_create_xmlid(
                                    sub_model_name, valitem[2], res_id
                                )
                                valitem[1] = xml_id
                        xml_ids.append(xml_id)
                        self.xmlid_cache[(sub_model_name, res_id)] = xml_id
                        childrecord = self._create_record(
                            doc, sub_model_name, valitem[2], xml_id
                        )
                        # do not use append here since childrecord is a list
                        record_list += childrecord
                    else:
                        pass

                if xml_ids:
                    # add field to parent record
                    field = doc.createElement("field")
                    field.setAttribute("name", key)
                    # field.setAttribute("ref", xml_ids)
                    # Add mode
                    field_data = ",\n".join(
                        map(
                            lambda x: INDENT * 4 + f"Command.link(ref('{x}'))",
                            xml_ids,
                        )
                    )
                    field.setAttribute(
                        "eval", "[\n" + field_data + "\n" + INDENT * 3 + "]"
                    )
                    record.appendChild(field)
            elif fields[key]["type"] in ("many2many",):
                sub_model_name = fields[key]["relation"]
                res = []
                for valitem in val or []:
                    if valitem[0] == 6:
                        for res_id in valitem[2]:
                            xml_id = self._get_xmlid(sub_model_name, res_id)
                            self.xmlid_cache[(sub_model_name, res_id)] = xml_id
                            res.append(xml_id)
                        if not res:
                            continue

                        field = doc.createElement("field")
                        field.setAttribute("name", key)
                        # Add mode
                        field_data = ",\n".join(
                            map(lambda x: INDENT * 4 + f"Command.link(ref('{x}'))", res)
                        )
                        field.setAttribute(
                            "eval", "[\n" + field_data + "\n" + INDENT * 3 + "]"
                        )
                        record.appendChild(field)
            else:
                field = doc.createElement("field")
                field.setAttribute("name", key)
                field.appendChild(doc.createTextNode(str(val)))
                record.appendChild(field)
        # add current record at the end of the list to ensure child records are before
        # parent records
        record_list.append(record)
        return record_list

    def _as_data(self, model_name, res_id, fields=None):  # noqa: C901
        result = {}
        if fields is None:
            fields = []
        Model = self.env[model_name]
        record_id = Model.browse(res_id)
        root_fields = [f[0] for f in fields]
        data = record_id.read(root_fields)[0]
        # data = record_id.with_context(name_create_enabled_fields=True).read(fields, load=None)[0]  # noqa: E501
        model_fields = Model.fields_get()
        for field_name in data.keys():
            if field_name in result:
                continue
            if model_fields[field_name]["type"] == "many2one":
                if isinstance(data[field_name], bool):
                    result[field_name] = data[field_name]
                elif not data[field_name]:
                    result[field_name] = False
                else:
                    result[field_name] = data[field_name][0]

            elif model_fields[field_name]["type"] in ("one2many",):
                sub_model_name = model_fields[field_name]["relation"]
                if len(data[field_name]):
                    # find sub-fields to export for this field
                    sub_fields = []
                    for f in fields:
                        if f[0] == field_name and isinstance(f, list):
                            if len(f) > 1:
                                sub_fields.append(f[1:])
                            else:
                                sub_fields = []
                                break
                    # process sub-records
                    sub_data_batch = []
                    for sub_res_id in data[field_name]:
                        if sub_model_name == model_name:
                            continue
                        sub_data = self._as_data(sub_model_name, sub_res_id, sub_fields)
                        sub_data_batch.append([0, 0, sub_data])
                    result[field_name] = sub_data_batch
                else:
                    result[field_name] = data[field_name]

            elif model_fields[field_name]["type"] == "many2many":
                result[field_name] = [(6, 0, data[field_name])]

            else:
                result[field_name] = data[field_name]
        # remove inherited fields (delegate inheritance)
        for v in Model._inherits.values():
            if v in result:
                del result[v]
        return result

    def generate_export_xml(self, model_name, fields, ids, import_compat):
        self.xmlid_cache = {}
        doc = minidom.Document()
        root = doc.createElement("odoo")
        doc.appendChild(root)
        field_names = [x["name"] for x in fields]
        fields_to_export = [fix_import_export_id_paths(f) for f in field_names]
        for res_id in ids:
            data = {}
            data = self._as_data(model_name, res_id, fields_to_export)
            xml_id = self._get_or_create_xmlid(model_name, data, res_id, import_compat)
            record_list = self._create_record(doc, model_name, data, xml_id)
            for record in record_list:
                root.appendChild(record)
        return self.to_string(doc)

    def to_string(self, doc):
        res = doc.toprettyxml(indent=INDENT).encode("utf-8")
        return res
