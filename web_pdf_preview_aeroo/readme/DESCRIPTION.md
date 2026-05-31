This module opens Aeroo-generated reports directly in the browser preview.

- It replaces the default download behavior for Aeroo reports with an inline
	preview flow.
- It keeps the standard report action workflow while improving readability for
	users who need to inspect documents quickly.

## Technical details

**Aeroo report controller override**

The module extends `report_aeroo` controller routes and reuses
`generate_aeroo_report` to return a response with an inline
`Content-Disposition` header, so the browser renders the report instead of
forcing a download.

**Preview route and frontend handler**

The module adds a dedicated `/report/preview_aeroo` route and registers an
`ir.actions.report` handler in backend assets. For actions with
`report_type == "aeroo"`, it builds the preview URL and opens it in a new tab
(or redirects on mobile).
