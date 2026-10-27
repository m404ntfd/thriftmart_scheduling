# ThriftMart Scheduling / Store Dispatch

A phone-friendly pickup and delivery schedule hosted on a Windows computer on the store's staff network.

[Download the latest Windows package](https://github.com/m404ntfd/thriftmart_scheduling/releases/latest)

## Start

1. Install Python 3.11 or newer, including the `py` launcher.
2. Extract the Windows ZIP to a permanent folder.
3. Run `Start-Store-Dispatch.bat` and leave it open.
4. On that PC visit `http://localhost:8080`, create the administrator, and add vehicles and employees.
5. On staff phones, use the local-network address printed in the server window.

Keep the computer awake. Allow access on the trusted private staff network only. Do not forward the server port to the Internet. This version uses local HTTP and is not designed for public or guest networks.

## Updates

Administrators use **Settings → Program updates → Check for updates → Install update & restart**. GitHub is already configured. Staff should save their appointments before an update; everyone signs in again afterward.

Upgrading from 0.1 requires one manual replacement of program files because that version has no updater. Preserve `data/`. See [RELEASE-GUIDE.txt](RELEASE-GUIDE.txt).

## Releases and data

The Actions workflow tests Windows and Linux and publishes both ZIPs on `main` when `VERSION` names an unpublished release. It also supports manual runs. Update release notes before increasing the version.

Customer data and accounts stay in `data/`, excluded from source and release packages. Daily backups live on the same disk; copy them to a separate protected drive. Update backups are retained separately.

Run tests with `python -m unittest test_server test_updater`. See [README.txt](README.txt) for complete operating instructions and pilot limitations.
