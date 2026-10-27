"""Build the exact ZIP asset consumed by the in-app GitHub updater."""
from pathlib import Path
import zipfile
import updater
root=Path(__file__).resolve().parent
updater.version(updater.current())
out=root/'dist';out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/updater.ASSET,'w',zipfile.ZIP_DEFLATED) as z:
    for name in updater.FILES:z.write(root/name,name)
print(out/updater.ASSET)

installer=out/('Store-Dispatch-Windows-v'+updater.current()+'.zip')
names=[*updater.FILES,'launcher.py','Start-Store-Dispatch.bat','RELEASE-GUIDE.txt','build_release.py','test_server.py','test_updater.py']
with zipfile.ZipFile(installer,'w',zipfile.ZIP_DEFLATED) as z:
    for name in names:z.write(root/name,'thrift-scheduler/'+name)
print(installer)
