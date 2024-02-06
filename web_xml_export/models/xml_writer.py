# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

import string
from xml.dom import minidom

from odoo import api, models
from odoo.tools import ustr
from odoo.models import fix_import_export_id_paths

DEFAULT_FIELDS = [
    "create_date",
    "create_uid",
    "display_name",
    "id",
    "__last_update",
    "write_date",
    "write_uid",
]
blank_dict = {}


class XElement(minidom.Element):
    """dom.Element with compact print
    The Element in minidom has a problem: if printed, adds whitespace
    around the text nodes. The standard will not ignore that whitespace.
    This class simply prints the contained nodes in their compact form, w/o
    added spaces.
    """

    def writexml(self, writer, indent="", addindent="", newl=""):
        writer.write(indent)
        minidom.Element.writexml(self, writer, indent="", addindent="", newl="")
        writer.write(newl)


def doc_createXElement(xdoc, tagName):
    e = XElement(tagName)
    e.ownerDocument = xdoc
    return e


class XmlWriter(models.Model):
    _name = "xml.writer"
    _description = "XML Writer"

    @api.model
    def _get_or_create_xmlid(self, model, data, res_id=False, import_compat=False):
        if res_id:
            if import_compat:
                self.env[model].browse(res_id).ensure_human_xml_id()
            xml_id = self._get_xmlid(model, res_id)
            if xml_id and xml_id[0]:
                return xml_id[0]
            xml_id = self.env[model]._compose_xml_record_human_name(
                res_id, data.get("name", "")
            )
        return xml_id

    @api.model
    def _get_xmlid(self, model, id):
        if isinstance(id, tuple):
            id = id[0]
        if (model, id) in blank_dict:
            res_id = blank_dict[(model, id)]
            return res_id, False
        dt = self.env["ir.model.data"]
        obj = dt.search([("model", "=", model), ("res_id", "=", id)])
        if not obj:
            return False, None
        obj = obj[0]
        depends = self._context.get("depends", {})
        depends[obj.module] = True
        return obj.module + "." + obj.name, obj.noupdate

    @api.model
    def _create_record(self, doc, model, data, record_id, noupdate=False):
        data_pool = self.env["ir.model.data"]
        model_pool = self.env[model]
        record = doc.createElement("record")
        record.setAttribute("model", model)
        record.setAttribute("id", record_id)
        record_list = [record]
        lids = data_pool.search([("model", "=", model)])
        lids = lids[:1]
        res = lids.read(["module"])
        depends = {}
        self = self.with_context({"depends": {}})
        # Add blank_dict to new self object
        if res:
            depends[res[0]["module"]] = True
        fields = model_pool.fields_get()
        for key, val in data.items():
            if key in DEFAULT_FIELDS:
                continue
            # functional fields check
            if (
                key in model_pool._fields.keys()
                and not model_pool._fields[key].store
                and not model_pool._fields[key].inverse
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
                field = doc.createElement("field")
                field.setAttribute("name", key)
                if type(val) in (type(""), type("")):
                    id = val
                else:
                    id, update = self._get_xmlid(fields[key]["relation"], val)
                    noupdate = noupdate or update
                if not id:
                    relation_pool = self.env[fields[key]["relation"]]
                    field.setAttribute("model", fields[key]["relation"])
                    # Ensure this model is namable
                    if relation_pool._rec_name:
                        fld_nm = relation_pool._rec_name
                        val = relation_pool.browse(val)
                        name = val.read([fld_nm])[0][fld_nm] or False
                        field.setAttribute("search", str([(str(fld_nm), "=", name)]))
                else:
                    field.setAttribute("ref", id)
                record.appendChild(field)
            elif fields[key]["type"] in ("one2many",):
                for valitem in val or []:
                    if (
                        valitem[0] in (0, 1)
                        and valitem[2].get("name") not in DEFAULT_FIELDS
                    ):
                        if valitem[0] == 0:
                            newid = self._get_or_create_xmlid(
                                fields[key]["relation"],
                                valitem[2],
                                valitem[2].get("id"),
                            )
                            valitem[1] = newid
                        else:
                            newid, update = self._get_xmlid(
                                fields[key]["relation"], valitem[1]
                            )
                            if not newid:
                                newid = self._get_or_create_xmlid(
                                    fields[key]["relation"], valitem[2]
                                )
                                valitem[1] = newid
                        blank_dict[(fields[key]["relation"], valitem[1])] = newid
                        childrecord, update = self._create_record(
                            doc, fields[key]["relation"], valitem[2], newid
                        )
                        noupdate = noupdate or update
                        record_list += childrecord
                    else:
                        pass
            elif fields[key]["type"] in ("many2many",):
                res = []
                for valitem in val or []:
                    if valitem[0] == 6:
                        for id2 in valitem[2]:
                            id, update = self._get_xmlid(fields[key]["relation"], id2)
                            blank_dict[(fields[key]["relation"], id2)] = id
                            res.append(id)
                            noupdate = noupdate or update
                        if not res:
                            continue
                        INDENT = "    "
                        field = doc.createElement("field")
                        field.setAttribute("name", key)
                        # Add mode
                        field_data = ",\n".join(
                            map(lambda x: INDENT * 4 + "(4, ref('%s'))" % (x,), res)
                        )
                        field.setAttribute(
                            "eval", "[\n" + field_data + "\n" + INDENT * 3 + "]"
                        )
                        # field.setAttribute(
                        #     "eval",
                        #     "[(6,0,[\n"
                        #     + ",\n".join(
                        #         map(lambda x: INDENT * 4 + "ref('%s')" % (x,), res)
                        #     )
                        #     + "\n"
                        #     + INDENT * 3
                        #     + "])]",
                        # )
                        record.appendChild(field)
            else:
                field = doc_createXElement(doc, "field")
                field.setAttribute("name", key)
                field.appendChild(doc.createTextNode(ustr(val)))
                record.appendChild(field)
        return record_list, noupdate

    @api.model
    def get_copy_data(self, model, id, result, fields=[]):
        res = []
        obj = self.env[model]
        data = obj.browse(id).read(fields)
        if isinstance(data, list):
            data = data[0]
        mod_fields = obj.fields_get()
        for key in data.keys():
            if key in result:
                continue
            if mod_fields[key]["type"] == "many2one":
                if isinstance(data[key], bool):
                    result[key] = data[key]
                elif not data[key]:
                    result[key] = False
                else:
                    result[key] = data[key][0]

            elif mod_fields[key]["type"] in ("one2many",):
                rel = mod_fields[key]["relation"]
                if len(data[key]):
                    res1 = []
                    for rel_id in data[key]:
                        res = [0, 0]
                        if rel == model:
                            continue
                        res.append(self.get_copy_data(rel, rel_id, {}))
                        res1.append(res)
                    result[key] = res1
                else:
                    result[key] = data[key]

            elif mod_fields[key]["type"] == "many2many":
                result[key] = [(6, 0, data[key])]

            else:
                result[key] = data[key]
        for v in obj._inherits.values():
            del result[v]
        return result

    @api.model
    def _create_function(self, doc, model, name, record_id):
        record = doc.createElement("function")
        record.setAttribute("name", name)
        record.setAttribute("model", model)
        record_list = [record]
        value = doc.createElement("value")
        value.setAttribute("eval", "[ref('%s')]" % (record_id,))
        value.setAttribute("model", model)
        record.appendChild(value)
        return record_list, False

    @api.model
    def _generate_object_xml(self, rec, recv, doc, result=None):
        record_list = []
        noupdate = False
        recording_data = self._context.get("recording_data", [])
        if rec[3] == "write":
            for id in rec[4]:
                id, update = self._get_xmlid(rec[2], id)
                noupdate = noupdate or update
                if not id:
                    continue
                record, update = self._create_record(doc, rec[2], rec[5], id)
                noupdate = noupdate or update
                record_list += record

        elif rec[4] in ("menu_create",):
            for id in rec[5]:
                id, update = self._get_xmlid(rec[3], id)
                noupdate = noupdate or update
                if not id:
                    continue
                record, update = self._create_function(doc, rec[3], rec[4], id)
                noupdate = noupdate or update
                record_list += record

        elif rec[3] == "create":
            id = self._get_or_create_xmlid(rec[2], rec[4])
            record, noupdate = self._create_record(doc, rec[2], rec[4], id)

            blank_dict[(rec[2], result)] = id
            record_list += record

        elif rec[3] == "copy":
            data = self.get_copy_data(rec[2], rec[4], rec[5])
            copy_rec = (rec[0], rec[1], rec[2], rec[3], rec[4], data, rec[5])
            rec = copy_rec
            rec_data = [
                (recording_data[0][0], rec, recording_data[0][2], recording_data[0][3])
            ]
            recording_data = rec_data
            id = self._get_or_create_xmlid(rec[2], rec[5], rec[4])
            record, noupdate = self._create_record(doc, rec[2], rec[5], id)
            blank_dict[(rec[2], result)] = id
            record_list += record
        return record_list, noupdate

    @api.model
    def _generate_assert_xml(self, rec, doc):
        pass

    @api.model
    def generate_export_xml(self, model, fields, ids, import_compat):
        global blank_dict
        blank_dict = {}
        doc = minidom.Document()
        root = doc.createElement("odoo")
        doc.appendChild(root)
        field_names = [x["name"] for x in fields]
        fields_to_export = [fix_import_export_id_paths(f) for f in field_names]
        basic_fields_to_export = [f[0] for f in fields_to_export]
        for id in ids:
            data = {}
            data = self.get_copy_data(model, id, data, basic_fields_to_export)
            xml_id = self._get_or_create_xmlid(model, data, id, import_compat)
            record_list, noupdate = self._create_record(doc, model, data, xml_id)
            for record in record_list:
                root.appendChild(record)

        res = doc.toprettyxml(indent="    ").encode("utf-8")
        return res

    @api.model
    def generate_xml(self):
        recording_data = self._context.get("recording_data", [])
        if recording_data:
            doc = minidom.Document()
            terp = doc.createElement("odoo")
            doc.appendChild(terp)
            for rec in recording_data:
                if rec[0] == "workflow":
                    rec_id, noupdate = self._get_xmlid(rec[1][2], rec[1][4])
                    if not rec_id:
                        continue
                    wkf = doc.createElement("workflow")
                    terp.appendChild(wkf)
                    wkf.setAttribute("model", rec[1][2])
                    wkf.setAttribute("action", rec[1][3])
                    if noupdate:
                        data.setAttribute("noupdate", "1")
                    wkf.setAttribute("ref", rec_id)
                if rec[0] == "query":
                    res_list, noupdate = self._generate_object_xml(
                        rec[1], rec[2], doc, rec[3]
                    )
                    data = doc.createElement("data")
                    if noupdate:
                        terp.setAttribute("noupdate", "1")
                    for res in res_list:
                        terp.appendChild(res)
                elif rec[0] == "assert":
                    pass
            return doc.toprettyxml(indent="\t").encode("utf-8")
