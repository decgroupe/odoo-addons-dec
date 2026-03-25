// Copyright (C) DEC SARL, Inc - All Rights Reserved.
// Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import {beforeEach, expect, queryAllTexts, test} from "@odoo/hoot";
import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
    pagerNext,
    pagerPrevious,
} from "@web/../tests/web_test_helpers";
import {orderedByCache} from "@web_form_orderedby/js/form_controller.esm";

// ------- models -------

class Partner extends models.Model {
    name = fields.Char();
    line_ids = fields.One2many({relation: "line", string: "Lines"});
    _records = [
        {id: 1, name: "Partner 1", line_ids: [1, 2, 3]},
        {id: 2, name: "Partner 2", line_ids: [4, 5, 6]},
    ];
    _views = {
        form: `
            <form>
                <field name="name"/>
                <field name="line_ids">
                    <list>
                        <field name="sequence" widget="handle"/>
                        <field name="name"/>
                        <field name="value"/>
                    </list>
                </field>
            </form>
        `,
    };
}

class Line extends models.Model {
    name = fields.Char({sortable: true});
    value = fields.Integer({sortable: true, string: "Value"});
    partner_id = fields.Many2one({relation: "partner"});
    sequence = fields.Integer();
    _records = [
        {id: 1, name: "Line B", value: 30, partner_id: 1, sequence: 1},
        {id: 2, name: "Line A", value: 10, partner_id: 1, sequence: 2},
        {id: 3, name: "Line C", value: 20, partner_id: 1, sequence: 3},
        {id: 4, name: "Line Z", value: 5, partner_id: 2, sequence: 1},
        {id: 5, name: "Line X", value: 15, partner_id: 2, sequence: 2},
        {id: 6, name: "Line Y", value: 25, partner_id: 2, sequence: 3},
    ];
}

defineModels([Partner, Line]);

// ------- helpers -------

beforeEach(() => {
    // Clear the module-level sort cache so tests don't pollute each other
    for (const key of Object.keys(orderedByCache)) {
        delete orderedByCache[key];
    }
});

function getLineNames() {
    return queryAllTexts(".o_field_widget[name=line_ids] .o_data_row td[name=name]");
}

// ------- tests -------

test("sort state is preserved when navigating to next/previous record", async () => {
    await mountView({
        resModel: "partner",
        type: "form",
        resId: 1,
        resIds: [1, 2],
    });
    // Initial order for partner 1
    expect(getLineNames()).toEqual(["Line B", "Line A", "Line C"]);
    // Sort ascending by name
    await contains(
        ".o_field_widget[name=line_ids] th.o_column_sortable[data-name=name]"
    ).click();
    expect(getLineNames()).toEqual(["Line A", "Line B", "Line C"]);
    // Navigate to partner 2
    await pagerNext();
    expect(getLineNames()).toEqual(["Line Z", "Line X", "Line Y"]);
    // Navigate back to partner 1 — sort must be restored
    await pagerPrevious();
    expect(getLineNames()).toEqual(["Line A", "Line B", "Line C"]);
});

test("sort state is preserved when returning from list view to form view", async () => {
    // Simulate the cache state as if the user had sorted line_ids by name asc
    // and then navigated away (onWillUnmount would have stored this)
    orderedByCache["partner,1"] = {line_ids: [{name: "name", asc: true}]};
    // Mount a fresh form view (simulates returning from list view)
    await mountView({
        resModel: "partner",
        type: "form",
        resId: 1,
        resIds: [1, 2],
    });
    // OnRootLoaded fires on mount and restores the cached sort
    expect(getLineNames()).toEqual(["Line A", "Line B", "Line C"]);
});

test("sort descending is preserved after record navigation", async () => {
    await mountView({
        resModel: "partner",
        type: "form",
        resId: 1,
        resIds: [1, 2],
    });
    // Sort ascending then descending by value
    await contains(
        ".o_field_widget[name=line_ids] th.o_column_sortable[data-name=value]"
    ).click();
    expect(getLineNames()).toEqual(["Line A", "Line C", "Line B"]);
    await contains(
        ".o_field_widget[name=line_ids] th.o_column_sortable[data-name=value]"
    ).click();
    expect(getLineNames()).toEqual(["Line B", "Line C", "Line A"]);
    // Navigate away and back
    await pagerNext();
    await pagerPrevious();
    // Descending sort must be restored
    expect(getLineNames()).toEqual(["Line B", "Line C", "Line A"]);
});
