This module improves the Unit of Measure search behavior to find relevant
results faster when users type the beginning of a unit name.

- Prioritizes exact and prefix matches on unit names.
- Keeps useful fallback behavior so broad searches still work.
- Returns results in a practical order for day-to-day data entry.

## Technical details

**Model extension**

The module extends uom.uom and defines a custom _name_search_order
(factor DESC, name) to control result ranking.

**Search strategy**

The name_search override keeps the standard super() result as fallback,
then applies a progressive search flow when a search term is provided:

- Step 1: exact case-insensitive match with =ilike.
- Step 2: prefix match with =ilike on name + %.
- Step 3: generic operator-based match when previous steps are not enough.

Each step excludes already collected ids and respects the requested limit.
When custom records are found, the method returns the same (id,
display_name) structure as base Odoo behavior.
