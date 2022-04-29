odoo.define('mail_activity_forecast_dhxgantt.MailActivityGanttRenderer', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var GanttRenderer = require('web_dhxgantt.GanttRenderer');
    var QWeb = core.qweb;

    var MailActivityGanttRenderer = GanttRenderer.extend({

        _createGanttItem: function (dataPoint, parentDataPoint) {
            var item = this._super(dataPoint, parentDataPoint);

            // Record data
            var rec = dataPoint.data;

            var rendered = QWeb.render('mail.activity.title', {
                type: rec.activity_type_id.data.display_name,
                columnTitle: item.columnTitle,
                icon: rec.icon,
                debug: session.debug,
            });

            // var type = rec.activity_type_id.data.display_name;
            // if (item.columnTitle && (item.columnTitle !== _t("Undefined"))) {
            //     item.columnTitle = `${type}:<small><b> ${item.columnTitle}</b></small>`;
            // } else {
            //     item.columnTitle = type;
            // }
            // item.columnTitle = `<i class="fa ${rec.icon}"></i> ${item.columnTitle}`;
            item.columnTitle = rendered;

            return item;
        },

    });

    return MailActivityGanttRenderer;

});