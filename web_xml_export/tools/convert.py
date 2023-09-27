from odoo.tools.convert import xml_import


def _tag_record(self, rec):
    try:
        res = original_tag_record(self, rec)
    except Exception as exception:
        ignore_exception = False
        if "Cannot update missing record" in exception.args[0]:
            for child in rec.iterchildren("field"):
                if child.get("name") == "xid":
                    rec.set("id", child.text)
                    res = original_tag_record(self, rec)
                    ignore_exception = True
        if not ignore_exception:
            raise exception
    return res


original_tag_record = xml_import._tag_record
xml_import._tag_record = _tag_record


def _test_xml_id(self, xml_id):
    if "." in xml_id:
        module, uuid = xml_id.split(".", 1)
        if module != self.module and module in ("__export__", "xml_export"):
            return
    original_test_xml_id(self, xml_id)


original_test_xml_id = xml_import._test_xml_id
xml_import._test_xml_id = _test_xml_id


def model_id_get(self, id_str, raise_if_not_found=True):
    try:
        res = original_model_id_get(self, id_str, raise_if_not_found)
    except ValueError as exception:
        ignore_exception = False
        if "External ID not found in the system" in exception.args[0]:
            if "." in id_str and "__" in id_str:
                module, uuid = id_str.split(".", 1)
                if module in ("__export__", "xml_export"):
                    model_id = uuid.split("__", 1)[0]
                    model, id = model_id.rsplit("_", 1)
                    model = model.replace("_", ".")
                    id = int(id)
                    if model in self.env:
                        instance_id = self.env[model].browse(id)
                        if instance_id.exists():
                            ignore_exception = True
                            res = (model, id)
        if not ignore_exception:
            raise exception
    return res


original_model_id_get = xml_import.model_id_get
xml_import.model_id_get = model_id_get
