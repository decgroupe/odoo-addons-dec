This module provides a `XML Data` model that allows storing and re-importing
Odoo XML data records directly from the database interface, making it easy to
prototype or replay configuration data without manipulating files on disk.

- Store XML data records with a name, module context, and raw XML content.
- Import stored XML in `init` or `update` mode with a single button click.
- Validate XML content against the Odoo RelaxNG schema before importing.

## Technical details

**xml.data model**

The `xml.data` model stores a raw XML string in the `content` field. The
`_import` method parses it via `lxml` and feeds it to `odoo.tools.convert.xml_import`
exactly as Odoo would when loading a regular data file, using the `module`
field as the module context. The `_check_xmldoc` helper validates the document
against the `import_xml.rng` RelaxNG schema shipped with Odoo, logging
detailed errors via `jingtrang` when available.
