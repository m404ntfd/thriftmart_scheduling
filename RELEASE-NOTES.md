# Thrift Mart Dispatch 0.8.1

- Mobile schedule at /mobile and /mobile/ on the same running dispatch server.
- Large Pickup and Delivery buttons, touch-friendly editing, daily/monthly views, search, and vehicle/status filters.
- Tap customer phone numbers to call and addresses to open Maps.
- Connection-loss warning, manual refresh, and refresh on returning to the browser.
- Same employee accounts, shared appointments, conflict checks, and administrator settings.

Existing servers can install this version using Settings → Check for server updates → Install update & restart. Phones then open http://SERVER-IP:8080/mobile on the staff Wi-Fi. No separate phone installation is needed. Native Windows applications remain unsigned; this update does not resolve Windows App Control publisher restrictions.

- Appointment phone numbers are required in the form and by the server.
- Separate street address, city, state, and ZIP fields. Older addresses are preserved and can be split when editing.
- Employee assignment dropdown supports multiple checkboxes, preserving previous assignments.
- Remote Manager has Manage employees to add/remove employee accounts. Removal revokes sessions and keeps appointment history; administrator accounts are protected.

Install the new unified Windows installer on Remote Manager computers to get the new native employee controls. The server/mobile changes can also be installed through the server update button.
