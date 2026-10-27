# Thrift Mart Dispatch 0.4.0

One Windows installer for **Thrift Mart Dispatch Server**, **Thrift Mart Dispatch Remote Manager**, or **Both**. Required runtime included; no separate Python installation needed.

- Server renamed and given a matching Start-menu shortcut.
- Native Remote Manager connects over the trusted staff network for status, backups, restart and GitHub server updates. Schedule and settings editing opens in the browser.
- Configurable OneDrive backup folder, hourly complete backups, manual backup button and last-result reporting. Backups include appointments, vehicles, employee accounts and settings. Keeps the latest 90 archives.
- Start-menu restore tool for disaster recovery. Validates backups, preserves existing data before replacement, and prevents restoring while the server is running.

Download **Thrift-Mart-Dispatch-Setup-v0.4.0.exe** on each computer and choose its role. The separate `Store-Dispatch-Update.zip` asset is for the built-in updater, not first-time installation.

For existing 0.2 users: close the server, preserve `data/`, and run the installer once to add the new launcher and restore utility. Install into the existing program folder or move the old data folder to the new one while stopped.

OneDrive handles cloud synchronization; the program confirms local backup creation only. Verify the OneDrive synced status before relying on off-computer recovery. Local HTTP, trusted staff network only. Unsigned installer. On-site network/phone testing remains necessary.
