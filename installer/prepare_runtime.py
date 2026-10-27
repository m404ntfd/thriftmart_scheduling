"""Copy only the standard Python runtime from the Windows build machine."""
import os,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];target=root/'runtime';target.mkdir(exist_ok=True)
source=Path(sys.base_prefix)
for pattern in ('python*.exe','*.dll','LICENSE*'):
 for p in source.glob(pattern):shutil.copy2(p,target/p.name)
for name in ('Lib','DLLs'):
 shutil.copytree(source/name,target/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('site-packages','__pycache__','test','tests','idlelib','turtledemo'))
version=f'python{sys.version_info.major}{sys.version_info.minor}'
(target/(version+'._pth')).write_text('.\nLib\nDLLs\n..\n',encoding='utf-8')
print('Prepared bundled standard library runtime:',target)
