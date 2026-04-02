import {CalendarCommonRenderer} from "@web/views/calendar/calendar_common/calendar_common_renderer";
import {CalendarRenderer} from "@web/views/calendar/calendar_renderer";
import {CalendarYearRenderer} from "@web/views/calendar/calendar_year/calendar_year_renderer";
import {onPatched} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";

const EXTRA_PROPS = {
    slotDuration: {type: String, optional: true},
    snapDuration: {type: String, optional: true},
};

patch(CalendarRenderer, {
    props: {...CalendarRenderer.props, ...EXTRA_PROPS},
});

patch(CalendarYearRenderer, {
    props: {...CalendarYearRenderer.props, ...EXTRA_PROPS},
});

patch(CalendarCommonRenderer, {
    props: {...CalendarCommonRenderer.props, ...EXTRA_PROPS},
});

patch(CalendarCommonRenderer.prototype, {
    setup() {
        super.setup();
        onPatched(() => {
            if (this.props.slotDuration) {
                this.fc.api.setOption("slotDuration", this.props.slotDuration);
            }
            if (this.props.snapDuration) {
                this.fc.api.setOption("snapDuration", this.props.snapDuration);
            }
        });
    },
    get options() {
        const options = super.options;
        if (this.props.slotDuration) {
            options.slotDuration = this.props.slotDuration;
        }
        if (this.props.snapDuration) {
            options.snapDuration = this.props.snapDuration;
        }
        return options;
    },
});
