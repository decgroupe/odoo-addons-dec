This module opens PDF reports directly in the browser preview instead of forcing a file download.

- Desktop users get the report in a new tab, so they can review or print it without leaving the current screen.
- Mobile users open the report in the current tab, which avoids popup restrictions on mobile browsers.

## Technical details

**Report action handler**

The module registers an `ir.actions.report handlers` entry in the web client and intercepts `qweb-pdf` report actions.

**URL generation**

The handler builds the report URL with `getReportUrl(action, "pdf", userContext)` so both direct-record reports and wizard-based reports keep their expected parameters.

**Desktop and mobile behavior**

Desktop browsers open the generated PDF URL in a new tab using `window.open`, while mobile user agents are redirected in-place through `window.location`.
