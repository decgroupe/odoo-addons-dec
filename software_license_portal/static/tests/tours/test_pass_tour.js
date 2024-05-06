
odoo.define("software_license_portal.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "mylicense_tour",
        {
            url: "/my/licenses",
            test: true
        },
        [
            {
                content: "Select Brick Game License with serial [BG-A03].",
                trigger: ".tr_slp_license_link:contains('BG-A03')",
            },
            {
                content: "Deactivate HID [0d:cc:49:c5:10:86].",
                trigger: ".tr_slp_license_hardware_identifier_name span:contains('0d:cc:49:c5:10:86')",
                run: function () {
                    $('.tr_slp_license_hardware_identifier_name:contains("0d:cc:49:c5:10:86")').parent().find("form").submit();
                },
            },
            {
                content: "Ensure no more activated hardware.",
                trigger: "div.alert.alert-warning:contains('There is no activated hardware on this license.')",
            },
        ]
    );

    tour.register(
        "mypass_tour",
        {
            url: "/my/passes",
            test: true
        },
        [
            {
                content: "Select Premium Pass with serial [9NENW-Y2XZT-3GA9C-0CD61].",
                trigger: ".tr_slp_license_pass_link:contains('9NENW-Y2XZT-3GA9C-0CD61')",
            },
            {
                content: "Deactivate HID [ab99c8ef7899f].",
                trigger: ".tr_slp_license_pass_hardware_group_name span:contains('ab99c8ef7899f')",
                run: function () {
                    $('.tr_slp_license_pass_hardware_group_name:contains("ab99c8ef7899f")').parent().find("form").submit();
                },
            }
        ]
    );

    tour.register(
        "mypass_no_hardware_tour",
        {
            url: "/my/passes",
            test: true
        },
        [
            {
                content: "Select Basic Pass with serial [MPUIF-K76R3-SKTJM-C091C].",
                trigger: ".tr_slp_license_pass_link:contains('MPUIF-K76R3-SKTJM-C091C')",
            },
            {
                content: "Ensure no activated hardware.",
                trigger: "div.alert.alert-warning:contains('There is no activated hardware on this pass.')",
            },
        ]
    );

});
