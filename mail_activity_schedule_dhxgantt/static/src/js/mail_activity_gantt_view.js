odoo.define('mail_activity_schedule_dhxgantt.MailActivityGanttView', function (require) {
    "use strict";

    var GanttView = require('web_dhxgantt.GanttView');
    var MailActivityGanttController = require('mail_activity_schedule_dhxgantt.MailActivityGanttController');
    var MailActivityGanttRenderer = require('mail_activity_schedule_dhxgantt.MailActivityGanttRenderer');
    var MailActivityGanttModel = require('mail_activity_schedule_dhxgantt.MailActivityGanttModel');

    var view_registry = require('web.view_registry');

    var MailActivityGanttView = GanttView.extend({
        config: _.extend({}, GanttView.prototype.config, {
            Controller: MailActivityGanttController,
            Renderer: MailActivityGanttRenderer,
            Model: MailActivityGanttModel,
        }),
    });

    view_registry.add('mail_activity_gantt', MailActivityGanttView);

    return MailActivityGanttView;

});