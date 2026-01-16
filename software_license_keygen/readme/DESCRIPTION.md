This module adds automatic and manual serial generation for Software License records.

- Adds an Auto-generate Serial option on software applications of type In-house.
- Automatically creates a formatted serial for standard licenses when enabled on the selected application.
- Adds a Generate Serial button on license forms so users can regenerate a serial on demand.
- Appends a checksum segment to each generated key to reduce accidental input errors.

## Technical details

**Software application configuration**

The module extends software.application with the boolean field auto_generate_serial.
The field is displayed on the Licensing page and is hidden when the application
type is not inhouse. The write override also forces auto_generate_serial to
False when the application type is changed away from inhouse.

**License serial generation flow**

The module extends software.license by overriding create, copy, and
onchange_application_id.

- create: when context force_generate_serial is set, a serial is generated for
	standard licenses with an empty serial; after creation, onchange_application_id
	is re-triggered when the serial still matches the default value.
- copy: generates a new serial when no serial is forced in defaults and the
	source application has auto_generate_serial enabled.
- onchange_application_id: updates serial on standard licenses when the linked
	application requires auto generation.

**Serial format and checksum**

Serials are built from an uppercase random key generated with key_generator,
excluding ambiguous characters such as O, then suffixed with a checksum. The
checksum is the first 5 uppercase hex characters of a SHA256 hash computed from
the serial content without separators.

**User interface integration**

The form view of software.license is extended with an object button,
action_generate_serial, placed after the serial field. The button is available
only on existing standard licenses and calls action_generate_serial to replace
the serial value.
