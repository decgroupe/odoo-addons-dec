odoo.define('mail_activity_schedule_dhxgantt.MailActivityGanttRenderer', function (require) {
    "use strict";

    var GanttRenderer = require('web_dhxgantt.GanttRenderer');

    var MailActivityGanttRenderer = GanttRenderer.extend({
        columnTitleTemplate: "mail_activity_schedule_dhxgantt.row.title",
    });

    return MailActivityGanttRenderer;

});