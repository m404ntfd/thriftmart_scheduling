THRIFT MART DISPATCH SERVER — 0.5.0

Use Thrift-Mart-Dispatch-Setup-v0.5.0.exe for a normal installation. Choose Server,
Remote Manager or Both. The installer includes the required Python runtime.
Open Thrift Mart Dispatch Server from the Start menu. Keep its window open.
First setup: http://localhost:8080 on the server PC. Create the administrator,
then add vehicles and employees. Phones use the staff-network address printed
in the server window. Allow the server on a trusted PRIVATE Windows network.

ONE DRIVE
Sign into OneDrive on the server. Settings > OneDrive backups & recovery lets
an administrator select a full LOCAL OneDrive folder path on the SERVER PC.
Enable hourly backups, save, and click Back up now to test. Latest 90 complete
ZIPs are retained. Backup includes schedule, accounts, vehicles, audit history,
GitHub repository setting and backup settings. Password hashes are included.
The program confirms a local save only. Confirm OneDrive has synced the file.
Failures and last-save information appear in Settings. Automatic backups run
only while the server is running; offline OneDrive uploads later when connected.
Do not place the live data folder itself in OneDrive.

RESTORE
On a replacement PC install Server, download a backup ZIP from OneDrive, and
close the server window. Open Restore Thrift Mart Dispatch Server from the
Start menu. Select the ZIP. Existing data is preserved in data/restore-safety.
Start the server, sign in using an account from the backup, then reconnect and
enable the new OneDrive backup folder. Restore disables automatic cloud backup
until you reconnect the folder to avoid writing to an old PC's path.

DATA AND UPDATES
Current data: data/schedule.db. Other settings: data/updates.json and
 data/backup-settings.json. Do not delete these during a program upgrade.
Administrator Settings > Program updates installs GitHub server updates.
Remote Manager can also initiate updates. Everyone signs in again after restart.
Use the unified installer again to update the Remote Manager or launcher.
Built-in code updates preserve installed launcher files and all customer data.

LOCAL NETWORK ONLY
Local HTTP is unencrypted. Use a trusted staff network, not guest Wi-Fi or the
Internet. Do not port-forward 8080. Server must remain powered on and awake.
Optional startup occurs after Windows sign-in; this is not a Windows service.
Remote Manager cannot power on the server or launch a stopped server.

SOURCE USERS
Python 3.11+ with the standard library can run launcher.py directly. The Windows
installer bundles Python, so installed users do not need to set that up.
The legacy Start-Store-Dispatch.bat remains an alias for the renamed launcher.

PASSWORDS
Administrators can change passwords in Settings > Employee accounts, or using
Change a user's password in Remote Manager. Both password entries must match.
The selected user is signed out everywhere. No password is recorded in the log.

UPDATE BUTTON
Use Update server in the administrator navigation, or open Manage or Update
Thrift Mart Dispatch Server from the Start menu for local administration.
