# Thrift Mart Dispatch 0.5.0

- Administrators can change an employee or administrator password in the server web interface under **Settings → Employee accounts → Change password**.
- Remote Manager has a native **Change a user’s password** button and user selector.
- Requires matching passwords of 8–256 characters. Password changes sign that user out on all devices, including the current session when changing your own password. The audit log records the action without storing the password.
- Added an administrator **Update server** button in the server navigation. It checks GitHub and offers **Install update & restart** when a newer version is available.
- The installer includes a **Manage or Update Thrift Mart Dispatch Server** shortcut. It opens local server administration with localhost selected, including server-update buttons.

Download **Thrift-Mart-Dispatch-Setup-v0.5.0.exe** and choose Server, Remote Manager, or Both. The runtime is bundled. Close the running server before running the installer and preserve the existing data folder.

Existing 0.4 servers can receive the server/web-interface changes using their in-app updater. Run the 0.5 installer on computers using Remote Manager to get its new native password controls and the new server administration shortcut. OneDrive backups and recovery remain available.
