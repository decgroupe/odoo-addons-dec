// Copyright (C) DEC SARL, Inc - All Rights Reserved.
// Written by Yann Papouin <ypa at decgroupe.com>, May 2026

import {browser} from "@web/core/browser/browser";
import {getReportUrl} from "@web/webclient/actions/reports/utils";
import {registry} from "@web/core/registry";
import {user} from "@web/core/user";

const reportHandlerRegistry = registry.category("ir.actions.report handlers");
const MOBILE_USER_AGENT = /Android|iPhone|iPad|iPod|Mobi/i;

reportHandlerRegistry.add("web_pdf_preview", async (action) => {
    if (action.report_type !== "qweb-pdf") {
        return false;
    }
    const userContext = {
        ...user.context,
    };

    if (action.context) {
        Object.assign(userContext, action.context);
    }
    const url = getReportUrl(action, "pdf", userContext);
    if (MOBILE_USER_AGENT.test(browser.navigator.userAgent)) {
        browser.location = url;
        return true;
    }
    const newWindow = browser.open(url, "_blank");
    if (!newWindow) {
        return false;
    }
    newWindow.document.title = "...";
    return true;
});
