This module lets you manage software licenses linked to your applications and customers.

- Create license records per application with a unique serial and activation identifier.
- Link licenses to customers and review all related licenses directly from the partner form.
- Track activated hardware identifiers for each license, including device information extracted from activation payloads.
- Define a license template on each software application to speed up creation of new licenses.

## Technical details

**License management**

The module adds the `software.license` model with mail thread support, unique serials per application, computed display names, export helpers, and activation methods that create `software.license.hardware` records when a new hardware identifier is received.

**Hardware tracking**

The `software.license.hardware` model stores hardware identifiers attached to a license and computes device name, domain, and FQDN from the JSON activation payload stored in the `info` field.

**Application integration**

The `software.application` model is extended with an integer application identifier and a `template_id` field pointing to a template license. The module also provides an action that creates a template license with `default_type=template`.

**Partner integration**

The `res.partner` model gains computed `license_ids` and `license_count` fields. The lookup aggregates licenses on the commercial entity using a `child_of` domain and limits results to in-house software applications.
