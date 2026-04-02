import {Component, useState} from "@odoo/owl";
import {AttendeeCalendarController} from "@calendar/views/attendee_calendar/attendee_calendar_controller";
import {CalendarController} from "@web/views/calendar/calendar_controller";
import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";

const LS_KEY_SLOT_DURATION = "calendar.slotDuration";
const LS_KEY_SNAP_DURATION = "calendar.snapDuration";

export class CalendarOptionsPanel extends Component {
    static template = "web_calendar_options.CalendarOptionsPanel";
    static props = {
        slotDuration: String,
        snapDuration: String,
        isWeekendVisible: Boolean,
        setSlotDuration: Function,
        setSnapDuration: Function,
        toggleWeekendVisibility: Function,
    };
    get title() {
        return _t("Options");
    }
    get labelWeekends() {
        return _t("Show Weekends");
    }
    get labelSlotDuration() {
        return _t("Slot Duration");
    }
    get labelSnapDuration() {
        return _t("Snap Duration");
    }
    get slotIntervals() {
        return [
            ["00:05:00", _t("5 min")],
            ["00:10:00", _t("10 min")],
            ["00:15:00", _t("15 min")],
            ["00:30:00", _t("30 min")],
            ["01:00:00", _t("1 hour")],
        ];
    }
    onSlotDurationChange(ev) {
        this.props.setSlotDuration(ev.target.value);
    }
    onSnapDurationChange(ev) {
        this.props.setSnapDuration(ev.target.value);
    }
    onWeekendToggle() {
        this.props.toggleWeekendVisibility();
    }
}

patch(CalendarController, {
    components: {
        ...CalendarController.components,
        OptionsPanel: CalendarOptionsPanel,
    },
});

patch(AttendeeCalendarController, {
    components: {
        ...AttendeeCalendarController.components,
        OptionsPanel: CalendarOptionsPanel,
    },
});

patch(CalendarController.prototype, {
    setup() {
        super.setup();
        this.calendarOptionsState = useState({
            slotDuration:
                browser.localStorage.getItem(LS_KEY_SLOT_DURATION) || "00:30:00",
            snapDuration:
                browser.localStorage.getItem(LS_KEY_SNAP_DURATION) || "00:15:00",
        });
    },
    setSlotDuration(value) {
        this.calendarOptionsState.slotDuration = value;
        browser.localStorage.setItem(LS_KEY_SLOT_DURATION, value);
    },
    setSnapDuration(value) {
        this.calendarOptionsState.snapDuration = value;
        browser.localStorage.setItem(LS_KEY_SNAP_DURATION, value);
    },
    get rendererProps() {
        const props = super.rendererProps;
        props.slotDuration = this.calendarOptionsState.slotDuration;
        props.snapDuration = this.calendarOptionsState.snapDuration;
        return props;
    },
    get optionsPanelProps() {
        return {
            slotDuration: this.calendarOptionsState.slotDuration,
            snapDuration: this.calendarOptionsState.snapDuration,
            isWeekendVisible: this.state.isWeekendVisible,
            setSlotDuration: this.setSlotDuration.bind(this),
            setSnapDuration: this.setSnapDuration.bind(this),
            toggleWeekendVisibility: this.toggleWeekendVisibility.bind(this),
        };
    },
});
