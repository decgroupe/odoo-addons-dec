import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("mylicense_tour", {
    url: "/my/licenses",
    steps: () => [
        {
            content: "Select Brick Game License with serial [BG-A03].",
            trigger: ".tr_slp_license_link:contains('BG-A03')",
            run: "click",
        },
        {
            content: "Deactivate HID [0d:cc:49:c5:10:86].",
            trigger:
                ".tr_slp_license_hardware_identifier_name span:contains('0d:cc:49:c5:10:86')",
            run() {
                this.anchor
                    .closest(".tr_slp_license_hardware_identifier_name")
                    .parentElement.querySelector("form button")
                    .click();
            },
            expectUnloadPage: true,
        },
        {
            content: "Ensure no more activated hardware.",
            trigger:
                "div.alert.alert-warning:contains('There is no activated hardware on this license.')",
        },
    ],
});

registry.category("web_tour.tours").add("mypass_tour", {
    url: "/my/passes",
    steps: () => [
        {
            content: "Select Premium Pass with serial [9NENW-Y2XZT-3GA9C-0CD61].",
            trigger: ".tr_slp_license_pass_link:contains('9NENW-Y2XZT-3GA9C-0CD61')",
            run: "click",
        },
        {
            content: "Deactivate HID [ab99c8ef7899f].",
            trigger:
                ".tr_slp_license_pass_hardware_group_name span:contains('ab99c8ef7899f')",
            run() {
                this.anchor
                    .closest(".tr_slp_license_pass_hardware_group_name")
                    .parentElement.querySelector("form button")
                    .click();
            },
        },
    ],
});

registry.category("web_tour.tours").add("mypass_no_hardware_tour", {
    url: "/my/passes",
    steps: () => [
        {
            content: "Select Basic Pass with serial [MPUIF-K76R3-SKTJM-C091C].",
            trigger: ".tr_slp_license_pass_link:contains('MPUIF-K76R3-SKTJM-C091C')",
            run: "click",
        },
        {
            content: "Ensure no activated hardware.",
            trigger:
                "div.alert.alert-warning:contains('There is no activated hardware on this pass.')",
        },
    ],
});
