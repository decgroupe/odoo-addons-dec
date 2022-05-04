odoo.define('mail_activity_forecast_dhxgantt.MailActivityGanttController', function (require) {
    "use strict";

    var GanttController = require('web_dhxgantt.GanttController');

    var MailActivityGanttController = GanttController.extend({

        _getGanttItemDialogActionParams: function (ganttItem, dataPoint, parentDataPoint, options) {
            var params = this._super(ganttItem, dataPoint, parentDataPoint);

            if (!ganttItem.isGroup) {
                // Record data
                var rec = dataPoint.data;

                // Override model and id to directly open the target object
                // of the `mail.activity`
                if (!options || (options && !options.noOverride)) {
                    params.res_model = rec["res_model"];
                    params.res_id = rec["res_id"];
                    params.view_id = false;
                }
            }

            return params;
        },

    });

    return MailActivityGanttController;

});