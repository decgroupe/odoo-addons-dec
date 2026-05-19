// Copyright (C) DEC SARL, Inc - All Rights Reserved.
// Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import {ActivityButton} from "@mail/core/web/activity_button";
import {ActivityListPopover} from "@mail/core/web/activity_list_popover";

import {Component} from "@odoo/owl";

import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {usePopover} from "@web/core/popover/popover_hook";

class ActivityButtonMy extends ActivityButton {
    static template = "mail_activity_my.ActivityButtonMy";

    get buttonClass() {
        const classes = [];
        switch (this.props.record.data.activity_my_state) {
            case "overdue":
                classes.push("text-danger");
                break;
            case "today":
                classes.push("text-warning");
                break;
            case "planned":
                classes.push("text-success");
                break;
            default:
                if (this.defaultActivityStateClass) {
                    classes.push(this.defaultActivityStateClass);
                }
                break;
        }
        const {activity_my_ids, activity_my_type_icon} = this.props.record.data;
        if (activity_my_ids?.records?.length) {
            classes.push(activity_my_type_icon || "fa-tasks");
        } else {
            classes.push(this.defaultActivityDecorationClass);
        }
        return classes.join(" ");
    }

    get title() {
        if (this.props.record.data.activity_my_summary) {
            return this.props.record.data.activity_my_summary;
        }
        if (this.props.record.data.activity_my_type_id) {
            return this.props.record.data.activity_my_type_id[1];
        }
        return _t("Show my activities");
    }

    async onClick() {
        if (this.popover.isOpen) {
            this.popover.close();
        } else {
            const resId = this.props.record.resId;
            this.popover.open(this.buttonRef.el, {
                activityIds: this.props.record.data.activity_my_ids.currentIds,
                onActivityChanged: () => {
                    this.props.record.load();
                    this.popover.close();
                },
                resId,
                resModel: this.props.record.resModel,
            });
        }
    }
}

class ListActivityButtonMy extends ActivityButtonMy {
    static props = {
        ...ActivityButtonMy.props,
        slots: Object,
    };
    static template = "mail_activity_my.ListActivityButtonMy";

    setup() {
        super.setup();
        this.popover = usePopover(ActivityListPopover, {position: "bottom-start"});
        this.defaultActivityStateClass = "";
        this.defaultActivityDecorationClass = "fa-clock-o";
    }
}

class KanbanActivityMy extends Component {
    static components = {ActivityButton: ActivityButtonMy};
    static fieldDependencies = [
        {name: "activity_my_state", type: "selection", selection: []},
        {name: "activity_my_type_icon", type: "char"},
        {name: "activity_my_ids", type: "one2many"},
        {
            name: "activity_my_type_id",
            type: "many2one",
            relation: "mail.activity.type",
        },
        {name: "activity_my_summary", type: "char"},
    ];
    static props = standardFieldProps;
    static template = "mail_activity_my.KanbanActivityMy";
}

class ListActivityMy extends Component {
    static components = {ActivityButton: ListActivityButtonMy};
    static fieldDependencies = [
        {name: "activity_my_state", type: "selection", selection: []},
        {name: "activity_my_type_icon", type: "char"},
        {name: "activity_my_ids", type: "one2many"},
        {
            name: "activity_my_type_id",
            type: "many2one",
            relation: "mail.activity.type",
        },
        {name: "activity_my_summary", type: "char"},
    ];
    static props = standardFieldProps;
    static template = "mail_activity_my.ListActivityMy";

    get summaryText() {
        if (this.props.record.data.activity_my_summary) {
            return this.props.record.data.activity_my_summary;
        }
        if (this.props.record.data.activity_my_type_id) {
            return this.props.record.data.activity_my_type_id[1];
        }
        return undefined;
    }
}

const kanbanActivityMy = {
    component: KanbanActivityMy,
    fieldDependencies: KanbanActivityMy.fieldDependencies,
};

const listActivityMy = {
    component: ListActivityMy,
    fieldDependencies: ListActivityMy.fieldDependencies,
    displayName: _t("My Next Activity"),
    supportedTypes: ["one2many"],
};

registry.category("fields").add("kanban_activity_my", kanbanActivityMy);
registry.category("fields").add("list_activity_my", listActivityMy);
