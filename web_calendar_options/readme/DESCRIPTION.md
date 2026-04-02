Adds an **Options** panel to the calendar sidebar so end-users can
customize rendering without leaving the view:

- **Show Weekends**: toggle Saturday and Sunday visibility in week and
  month views.
- **Slot Duration**: choose the height of each time slot in day/week
  views (5 min, 10 min, 15 min, 30 min, 1 hour).
- **Snap Duration**: choose the snapping interval when dragging or
  resizing events (same choices as slot duration).

Settings are persisted in `localStorage` and restored on the next
session automatically.

## Technical details

**Options panel**

A new OWL component `CalendarOptionsPanel` is registered and rendered
inside the calendar sidebar via an XML template inheritance on
`web.CalendarController` and `calendar.AttendeeCalendarController`.

**State management**

`CalendarController` is patched to add a reactive `calendarOptionsState`
object (using `useState`) that holds `slotDuration` and `snapDuration`.
Changes are written to `localStorage` (keys `calendar.slotDuration` and
`calendar.snapDuration`) so they survive page reloads.
The weekend toggle reuses the existing `toggleWeekendVisibility` method
already present in the base controller (which writes to `localStorage`
under `calendar.isWeekendVisible`).

**Renderer integration**

`CalendarCommonRenderer` is patched to read `slotDuration` and
`snapDuration` from its props and forward them to FullCalendar both at
initial render (via the `options` getter) and on subsequent re-renders
(via `onPatched`). `CalendarRenderer` and `CalendarYearRenderer` static
`props` are also patched to accept the two new optional props.
