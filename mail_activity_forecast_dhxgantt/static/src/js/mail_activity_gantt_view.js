odoo.define('mail_activity_forecast_dhxgantt.MailActivityGanttView', function (require) {
    "use strict";

    var GanttView = require('web_dhxgantt.GanttView');
    var MailActivityGanttController = require('mail_activity_forecast_dhxgantt.MailActivityGanttController');
    var GanttRenderer = require('web_dhxgantt.GanttRenderer');
    var MailActivityGanttModel = require('mail_activity_forecast_dhxgantt.MailActivityGanttModel');

    var view_registry = require('web.view_registry');

    var MailActivityGanttView = GanttView.extend({
        config: _.extend({}, GanttView.prototype.config, {
            Controller: MailActivityGanttController,
            Renderer: GanttRenderer,
            Model: MailActivityGanttModel,
        }),
    });

    view_registry.add('mail_activity_gantt', MailActivityGanttView);
    return MailActivityGanttView;

});