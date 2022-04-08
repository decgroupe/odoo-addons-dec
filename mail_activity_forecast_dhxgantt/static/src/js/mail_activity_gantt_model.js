odoo.define('mail_activity_forecast_dhxgantt.MailActivityGanttModel', function (require) {
    "use strict";

    var GanttModel = require('web_dhxgantt.GanttModel');

    var MailActivityGanttModel = GanttModel.extend({
        _getFields: function () {
            var values = this._super();
            values.push("res_id");
            values.push("res_model");
            values.push("activity_type_id");
            values.push("icon");
            // From `mail_activity_partner` module
            values.push("partner_id");
            // From `mail_activity_project` module
            values.push("project_id");
            return values;
        },
        createTask: function (rec, ganttGroups, groupBy, links, css_classes) {
            var task = this._super(rec, ganttGroups, groupBy, links, css_classes);
            task.overrideModelName = rec["res_model"];
            task.overrideModelId = rec["res_id"];
            var type = rec["activity_type_id"][1];
            if (task.columnTitle) {
                task.columnTitle = `${type}:<small><b> ${task.columnTitle}</b></small>`;
            } else {
                task.columnTitle = type;
            }
            task.columnTitle = `<i class="fa ${rec["icon"]}"></i> ${task.columnTitle}`;
            return task;
        }
    });
    return MailActivityGanttModel;

});