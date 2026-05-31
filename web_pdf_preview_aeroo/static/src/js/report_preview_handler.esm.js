// Copyright (C) DEC SARL, Inc - All Rights Reserved.
// Written by Yann Papouin <ypa at decgroupe.com>, May 2026
/* global URLSearchParams */
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";

const reportHandlerRegistry = registry.category("ir.actions.report handlers");
const MOBILE_USER_AGENT = /Android|iPhone|iPad|iPod|Mobi/i;

reportHandlerRegistry.add("web_pdf_preview_aeroo", async (action) => {
    if (action.report_type !== "aeroo") {
        return false;
    }
    const actionContext = action.context || {};
    const params = new URLSearchParams({
        report_id: String(action.id),
        record_ids: JSON.stringify(actionContext.active_ids || []),
        context: JSON.stringify(actionContext),
        action_context: JSON.stringify(actionContext),
        action_data: JSON.stringify(action.data || {}),
        token: String(Date.now()),
        debug: "true",
    });
    const url = `/report/preview_aeroo?${params.toString()}`;
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
