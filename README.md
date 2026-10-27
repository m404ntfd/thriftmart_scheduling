# Thrift Mart Dispatch

[Download the single Windows installer](https://github.com/m404ntfd/thriftmart_scheduling/releases/latest)

The installer offers **Server**, **Remote Manager**, or **Both**, with the required runtime bundled. Windows x64; no separate Python installation needed. It installs for the current Windows user.

## Store computer: Server

Choose **Thrift Mart Dispatch Server**, then open its Start-menu shortcut and keep it running. On that PC visit `http://localhost:8080` to create the first administrator. Add vehicles and employees in Settings. Phones use the staff-network address printed in the server window.

## Other computer: Remote Manager

Run the same installer and select **Thrift Mart Dispatch Remote Manager**. Enter the server IP/computer name and port (for example `192.168.1.50:8080`), test the connection, and sign in with a server administrator account. The native panel manages status, complete backups, restart and GitHub server updates. Schedule/account editing opens in the default browser and requires a separate browser sign-in.

## OneDrive backup

On the server, sign into OneDrive. In **Settings → OneDrive backups & recovery**, enter a folder inside that computer's OneDrive (a suggested path appears if Windows provides one), enable hourly backups, save, and click **Back up to OneDrive now**.

Each ZIP contains the schedule database (appointments, accounts, vehicles and audit history), GitHub updater settings and backup settings. The latest 90 archives are kept. Backups run hourly while the server is running. Failures and the last local save appear in Settings. A local save does not prove cloud sync: confirm OneDrive shows the file synced. Copying live database files into OneDrive is not used.

## Recovery on a replacement PC

1. Install the Server with the same installer and sign into OneDrive.
2. Download a complete backup ZIP locally from OneDrive.
3. Close the server window. Open **Restore Thrift Mart Dispatch Server** in the Start menu.
4. Select the ZIP and confirm replacement. Current data is kept in a local safety folder first.
5. Start the server and sign in using an account from the backup. Reconnect and enable the new PC's OneDrive folder in Settings.

## Existing 0.2 users

Close the server and keep a separate copy of `data/`. Install the Server into the existing program folder, or copy `data/` into the new installation folder while the server is stopped. This one-time installer upgrade adds the launcher, renamed shortcuts and restore tool. Later server code updates can use Settings or Remote Manager; updating the Remote Manager/installer requires rerunning the latest unified installer.

The legacy update asset remains named `Store-Dispatch-Update.zip` for compatibility. Program code updates do not overwrite customer data. The uninstaller leaves runtime-generated data and external backups in place.

## Operating limits

Use trusted staff networking only; local HTTP is unencrypted. Do not forward the port to the Internet. Remote Manager cannot turn on a PC or start a stopped server. Keep the server awake; optional automatic startup occurs after Windows sign-in, not before. The installer is unsigned. OneDrive must be running and signed in to sync the backup folder.

Run `python -m unittest test_server test_updater test_remote` for API, update, access-control and backup/restore tests. CI also builds the Windows executable/installer, checks GUI startup and tests an installed server with bundled Python.

## Administrator password changes and server updates

Server interface: **Settings → Employee accounts → Change password**. Remote Manager: **Change a user’s password**. Select the user and enter/confirm the new password. This signs the affected user out on all devices; administrators changing their own password sign in again too. Passwords are never shown in the activity log.

The server navigation includes **Update server**, which checks GitHub and offers installation when a newer release is available. The Server install also adds a **Manage or Update Thrift Mart Dispatch Server** Start-menu shortcut with native update controls pointed at localhost. If using a custom port, edit the address before connecting.

Use the unified installer to update Remote Manager itself; the server-update action updates server code only.
