This module provides a convenient way to view and manage XML-IDs (external identifiers) for Odoo records.

- Provides developer tools to programmatically create XML-IDs for existing records
- Automatically creates XML-IDs for parent records when using the _inherits mechanism

## Technical details

**Feature: Programmatic XML-ID Creation**

The module extends the `ir.model.data` model with new methods:
- `id_to_xmlid()`: Creates an XML-ID for a record specified by model and ID
- `record_to_xmlid()`: Creates an XML-ID for a record object
- `get_xmlid()`: Retrieves the module and name components of a record's XML-ID
- `get_xmlid_as_string()`: Returns the full XML-ID as a string
- `_create_parents_xmlid()`: Automatically creates XML-IDs for parent records

**Feature: Parent Record Handling**

When creating an XML-ID for a record that uses the _inherits mechanism, the module automatically creates corresponding XML-IDs for all parent records, ensuring consistent referencing across the inheritance chain.
