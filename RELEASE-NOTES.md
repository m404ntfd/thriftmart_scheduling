# Thrift Mart Dispatch 0.6.0

- Added a native **Thrift Mart Dispatch Server** desktop window with a white box-truck icon.
- The server shortcut, application window, taskbar and system tray use the truck icon.
- Minimize, the window's X button, and **Minimize to tray** hide the window while keeping the server running.
- Double-click the truck tray icon to reopen. Right-click for the server window, schedule, administration/update controls, or **Exit server**.
- Exit confirms and shuts down the server safely. Closing Remote Manager continues to leave the server running.
- Server console output is captured in `data/server-console.log`, accessible through **Open server log**.

Run **Thrift-Mart-Dispatch-Setup-v0.6.0.exe** once on the server computer to install the new desktop/tray host and shortcuts. Stop the previous server before upgrading; preserve the existing data folder. A server-code-only update cannot install the new desktop executable.

If Windows hides the tray icon, look under the taskbar's hidden-icons arrow. Keeping the server in the tray does not prevent Windows from sleeping; keep the server PC awake. Runtime is bundled in the unified installer.
