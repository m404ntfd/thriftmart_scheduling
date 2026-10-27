Store Dispatch 0.2.0 adds administrator-controlled GitHub updates.

- Settings shows the installed version, release notes, and Check for updates.
- Install update & restart verifies the GitHub asset checksum and preserves local scheduling data.
- Program files and database are backed up before installation.
- A launcher restores previous program files if the updated server fails its startup check.
- The release repository is preconfigured as m404ntfd/thriftmart_scheduling.

First installation or upgrade from 0.1: download the Windows ZIP, extract it, keep the existing data folder, and run Start-Store-Dispatch.bat. Python 3.11+ is required. Later versions can be installed from Settings.

This is a trusted-local-network pilot. Actual phone layout and on-site Windows operation still require testing. No road access or encrypted local HTTP is included. See RELEASE-GUIDE.txt for update limitations and recovery.
