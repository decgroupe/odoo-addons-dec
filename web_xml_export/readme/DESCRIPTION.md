This module adds an XML export format to the standard Odoo export dialog.

- XML export: users can export any list view data to a structured XML file
  directly from the export window, in addition to the existing CSV/XLSX formats.

## Technical details

**XML format option**

Extends `/web/export/formats` (via `ExportAddXMLSupport` controller) to append
an `{"tag": "xml", "label": "XML"}` entry to the list of available formats.

**XML generation endpoint**

A new HTTP route `/web/export/xml` (`XMLExport` controller) handles the export
request. It resolves record IDs from the given domain when no explicit IDs are
provided, then delegates generation to `ExportXmlWriter`.

**ExportXmlWriter**

Builds the XML document using Python's `xml.dom.minidom`. For each exported
record it calls `IrModelData.res_id_to_xmlid` (model extension on
`ir.model.data`) to resolve or generate human-readable XML IDs, then creates
`<record>` elements with `<field>` children matching the exported field list.
Many2one, One2many/Many2many, and selection fields are handled with specific
serialisation logic.
