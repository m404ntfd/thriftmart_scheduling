# Thrift Mart Dispatch 0.7.0

- Added **Thrift Mart Dispatch Server Console**: the actual command window has the white box-truck icon in its title bar/taskbar and a matching system-tray icon.
- Minimizing this command window hides it in the tray while the schedule remains available. Double-click the truck icon to restore the command window.
- Right-click the tray icon for the schedule, administrator/update controls, or **Exit server**.
- Older startup batch files now launch this console/tray version when installed. The graphical Server shortcut remains available as an alternative; only one server instance runs at a time.
- The console title-bar X is disabled to avoid accidental shutdown. Use **Exit server** in the tray menu to stop it safely.

Run **Thrift-Mart-Dispatch-Setup-v0.7.0.exe**, selecting Server or Both. Exit the current server first and retain its data folder. After installation, use **Thrift Mart Dispatch Server Console** from the Start menu or the existing startup batch file.

The Console shortcut uses Windows Console Host so its icon and minimize behavior can be controlled independently of Windows Terminal tabs. No global Windows Terminal settings are changed. This update requires the full installer; code-only updates do not add the console executable.
