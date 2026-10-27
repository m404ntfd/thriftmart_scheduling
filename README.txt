STORE DISPATCH — version 0.2.0 / local-network pilot

A phone-friendly shared pickup and delivery schedule for a Windows store computer.
Includes administrator GitHub release updates (see RELEASE-GUIDE.txt).
No subscription or third-party Python packages are required. Source code is included.

FIRST SETUP
1. Install Python 3.11 or newer from https://www.python.org/downloads/windows/
   Include the Python launcher (py). This package does not include Python.
2. Extract this entire folder to a permanent location, such as C:\StoreDispatch.
   Do not run it inside the ZIP. Do not put the database in a network/OneDrive folder.
3. Double-click Start-Store-Dispatch.bat and keep its window open.
4. On that same computer open http://localhost:8080 in a browser.
5. Create the administrator account with a unique password (at least 8 characters).
6. In Settings, add your actual vehicle names and employee accounts.
7. If Windows Firewall prompts, allow Python on PRIVATE networks only.
8. Connect phones to the same trusted staff Wi-Fi. Open the Wi-Fi address printed
   in the server window, for example http://192.168.1.50:8080 (use YOUR address).
   Guest Wi-Fi often blocks access. Staff sign in using their own accounts.
9. Bookmark that address on each phone. Use a browser home-screen shortcut where
   supported. This is a mobile website, not an installed/offline app.

EVERYDAY USE
- Day schedule is the default. Choose a date, vehicle filter, or search term.
- Add pickup / delivery collects customer, phone, address, items, start/end,
  vehicle, employees and notes. Address and items are required.
- Open any appointment to change it, mark it complete/canceled, or remove it.
- Active overlapping bookings for the same vehicle are blocked. End times may
  touch. Allow travel/loading time in the booking window; no route calculation.
- Every signed-in employee can view, add, edit and remove jobs.
- Only the administrator can add vehicles/accounts and view recent changes.
- Cancel keeps details. Remove permanently deletes the appointment details;
  the recent-changes log records the action and customer name.
- Other phones refresh about every 10 seconds. An open edit form stays as-is.
  If another employee changed the same job, saving is rejected: close, reopen
  the appointment and reapply your edits.
- All date/time entries are store wall-clock times. Use the same time zone on
  the server and phones. This first version does not support multiple zones.
- Sessions last 12 hours; restarting the server signs everyone out.

KEEPING IT RUNNING
Set Windows power settings to prevent sleep while plugged in. The screen may turn
 off. Start the batch file after restarting Windows. To start after staff signs in,
create a shortcut to the batch file and place that shortcut in shell:startup
(Win+R, type shell:startup). This is NOT a background Windows service and does not
start before Windows sign-in. Closing the server window stops the app.
Ask your network administrator for a DHCP reservation for this PC so its address
stays the same. Do not open/forward port 8080 to the Internet.

BACKUP / RESTORE
Database: data\schedule.db. Automatic daily snapshots are created while the server
is running in data\backups, checked hourly; the last 30 dated snapshots are kept.
These snapshots live on the SAME disk. Copy backups to a separate protected drive
regularly. They contain customer details and account password hashes.
To restore: stop the server, keep a separate copy of the current schedule.db,
copy the desired dated backup to data\schedule.db, then restart. This restores
ALL jobs, accounts and vehicles to that snapshot. Never replace a running DB.

PILOT LIMITATIONS
This build uses local HTTP, so traffic is not encrypted. Use only a trusted,
restricted staff network and unique app passwords. Before road access, add HTTPS
and a secure remote-access design; do not expose this server publicly. Internet
is not needed for local scheduling. No offline editing, email/text notifications,
password reset screen, account removal screen or vehicle rename/removal screen
is included in this first version. No customer records are preloaded.
An administrator password reset requires local maintenance; keep it securely.

This package was tested for API scheduling behavior in a Linux environment.
Windows startup and actual phone/browser layouts still need an on-site pilot.
Try sample appointments on two phones before using live customer data.

DEVELOPER NOTES
Python standard library HTTP server + SQLite, no external runtime packages.
Run: python launcher.py. Default port 8080; DISPATCH_PORT overrides it.
DISPATCH_DATA selects an alternate data folder for tests. Do not share it
between running server instances. Test with: python test_server.py.
