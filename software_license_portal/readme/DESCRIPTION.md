This module gives customers a self-service portal for software licenses and license passes.

- Shows only eligible licenses and passes for the current customer company in portal pages.
- Adds dedicated portal pages to browse, search, and sort licenses and passes.
- Lets portal users deactivate hardware activations from their account.
- Exposes API endpoints to activate, validate, deactivate, and list licenses from client applications.
- Adds a publish toggle on software applications to control whether related licenses are visible in the portal.

## Technical details

**Portal visibility and domains**

The module extends `software.application` with `portal_published` and extends
`software.license` with a stored related field of the same name. It overrides
default domain helpers to restrict portal content to company-related partners,
published applications, and in-house application type.

**Portal controllers**

`LicenseCustomerPortal` and `LicensePassCustomerPortal` add `/my/licenses` and
`/my/passes` listing/detail pages, with searchbar filters, sorting, and portal
counters. Access checks rely on record-level checks before rendering details.

**Activation management**

Portal POST routes allow deactivation of hardware activations for both
individual licenses and license passes. The model methods `deactivate()`
perform unlink operations and log actions.

**HTTP API endpoints**

`SoftwareLicenseController` provides JSON endpoints under `/api/license/v1`
for single and batch activation/validation/deactivation flows, request info
inspection, and license export by hardware or identifier. Responses include
structured status messages, remaining activations, and expiration metadata.
