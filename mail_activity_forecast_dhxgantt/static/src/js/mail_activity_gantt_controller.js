odoo.define('mail_activity_forecast_dhxgantt.MailActivityGanttController', function (require) {
    "use strict";

    var GanttController = require('web_dhxgantt.GanttController');

    var MailActivityGanttController = GanttController.extend({

        _getGanttItemDatabaseModelAndID: function (ganttItem, dataPoint, parentDataPoint) {
            var res = this._super(ganttItem, dataPoint, parentDataPoint);

            if (!ganttItem.isGroup) {
                // Record data
                var rec = dataPoint.data;

                // Override model and id to directly open the target object
                // of the `mail.activity`
                res.model = rec["res_model"];
                res.id = rec["res_id"];
            }

            return res;
        },

    });

    return MailActivityGanttController;

});