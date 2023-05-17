Keep only first two digits to split records

eg: If you have a city named Town with three zip codes (53000, 53001, 44000) then
that's probably an error and two cities shares the same name. If you execute the
split action, you will have two cities:

- Town (53000, 53001)
- Town (44000)
