This module integrates project scheduling with sales timesheet projects by preventing scheduling of projects when all their associated contracts are in a terminal state (done or cancelled).

- **Contract-aware scheduling**: Projects with contracts in final states (done or cancelled) cannot be scheduled.

## Technical details

**Scheduling Integration**

The module overrides the `_is_schedulable()` method on `project.project` to add contract state validation. After checking the base schedulability criteria, it verifies that not all contracts are in a terminal state before allowing a project to be scheduled. Additionally, the `_compute_schedulable` field depends on contract state changes to ensure the schedulable status is recomputed whenever contracts change state.
