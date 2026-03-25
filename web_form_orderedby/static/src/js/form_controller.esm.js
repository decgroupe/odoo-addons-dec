// Copyright (C) DEC SARL, Inc - All Rights Reserved.
// Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import {FormController} from "@web/views/form/form_controller";
import {browser} from "@web/core/browser/browser";
import {onWillUnmount} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

// Module-level cache: persists across component remounts (list→form navigation).
// exported so that tests can reset it between runs.
export const orderedByCache = {};

patch(FormController.prototype, {
    setup() {
        super.setup();
        browser.console.debug("FormController setup, initializing orderedBy state");
        // Save sort state when leaving the form view (e.g. back to list)
        onWillUnmount(() => {
            this._saveOrderedBy();
            browser.console.debug("WillUnmount, saved orderedBy state", orderedByCache);
        });
        // Chain into model's onRootLoaded hook to restore sort after reload
        const originalOnRootLoaded = this.model.hooks.onRootLoaded;
        this.model.hooks.onRootLoaded = async () => {
            await originalOnRootLoaded();
            await this._restoreOrderedBy();
        };
    },

    onWillLoadRoot(...args) {
        // Save current x2many sort state before the root record reloads
        this._saveOrderedBy();
        browser.console.debug("WillLoadRoot, saved orderedBy state", orderedByCache);
        return super.onWillLoadRoot(...args);
    },

    _getFormKey() {
        // Generate a unique key based on model name and record id
        const root = this.model.root;
        return `${root.resModel},${root.resId}`;
    },

    _saveOrderedBy() {
        // Snapshot the orderBy of each x2many list for the current record
        const root = this.model && this.model.root;
        if (!root || !root.resId) {
            browser.console.debug(
                "No root or root without id, skipping orderedBy save"
            );
            return;
        }
        const formKey = this._getFormKey();
        for (const [fieldName, fieldValue] of Object.entries(root.data)) {
            if (
                fieldValue &&
                typeof fieldValue.load === "function" &&
                Array.isArray(fieldValue.orderBy) &&
                fieldValue.orderBy.length
            ) {
                if (!orderedByCache[formKey]) {
                    orderedByCache[formKey] = {};
                }
                orderedByCache[formKey][fieldName] = [...fieldValue.orderBy];
            }
        }
        browser.console.debug("Saved orderedBy for", formKey, orderedByCache[formKey]);
    },

    async _restoreOrderedBy() {
        browser.console.debug("Restoring orderedBy if needed for", this._getFormKey());
        // Re-apply the saved x2many sort orders after a record reload
        const root = this.model && this.model.root;
        if (!root || !root.resId) {
            browser.console.debug(
                "No root or root without id, skipping orderedBy restore"
            );
            return;
        }
        const formKey = this._getFormKey();
        const sortState = orderedByCache[formKey];
        if (!sortState) {
            browser.console.debug(
                "No saved orderedBy state for",
                formKey,
                "skipping restore"
            );
            return;
        }
        for (const [fieldName, orderBy] of Object.entries(sortState)) {
            const list = root.data[fieldName];
            if (
                list &&
                typeof list.load === "function" &&
                Array.isArray(list.orderBy) &&
                orderBy.length &&
                JSON.stringify(list.orderBy) !== JSON.stringify(orderBy)
            ) {
                // Use _sort (not load) so records are actually re-sorted, not
                // just the config's orderBy updated (which only shows the arrow)
                await list._sort(list.currentIds, orderBy);
            }
        }
        browser.console.debug("Restored orderedBy for", formKey, sortState);
    },
});
