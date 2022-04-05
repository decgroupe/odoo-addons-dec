odoo.define('mail_activity_forecast_dhxgantt.MailActivityGanttModel', function (require) {
    "use strict";

    var GanttModel = require('web_dhxgantt.GanttModel');

    var MailActivityGanttModel = GanttModel.extend({
        _getFields: function () {
            var values = this._super();
            values.push("res_id");
            values.push("res_model");
            values.push("activity_type_id");
            return values;
        },
        create_task: function (rec, ganttGroups, groupBy, links, css_classes) {
            var task = this._super(rec, ganttGroups, groupBy, links, css_classes);
            task.overrideModelName = rec["res_model"];
            task.overrideModelId = rec["res_id"];
            return task;
        }
    });
    return MailActivityGanttModel;

});