This module allows you to set a custom starting number for Odoo sequences that use date ranges, instead of always starting at 1 after each range reset.

- Define a custom "First Number" on any sequence: when a new date range is created (e.g., a new month or year), the sequence will start from the configured value rather than the default 1.
- Fallback logic ensures a sensible default is used when no explicit first number is configured.

## Technical details

**Custom first number field**

A new `number_first` (integer) field is added to `ir.sequence` via inheritance, with a default value of 1. The field is displayed in the sequence form view just before the `number_increment` field, but only when the "Use Date Range" option is enabled on the sequence.

**Override of `_create_date_range_seq`**

The method `_create_date_range_seq` on `ir.sequence` is overridden. After the super call creates the new date range record, `number_next` on that range is set to `self.number_first` if that field has a truthy value; otherwise it falls back to `self.number_next_actual`, and finally to `1` as a last resort. This guarantees that the first number of each new date range respects the user's preference.
