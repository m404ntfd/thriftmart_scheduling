"""Verify an installed server runs with bundled Python and the manager connects."""
import os,sys,subprocess,tempfile,socket,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'remote'))
from client import Client
root=Path(sys.argv[1])
with tempfile.TemporaryDirectory() as data:
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 p=subprocess.Popen([str(root/'runtime/python.exe'),str(root/'launcher.py')],cwd=root,env={**os.environ,'DISPATCH_DATA':data,'DISPATCH_PORT':str(port)})
 try:
  c=Client(f'127.0.0.1:{port}')
  for i in range(60):
   try:c.probe();break
   except Exception:time.sleep(.25)
  else:raise AssertionError('Installed server did not start')
  c.request('setup',{'name':'SmokeAdmin','password':'TestPasswordOnly'})
  assert c.login('SmokeAdmin','TestPasswordOnly')['name']=='Thrift Mart Dispatch Server'
  c.request('admin/restart',{})
  time.sleep(2)
  assert c.probe()['application']=='thrift-mart-dispatch'
  print('Bundled server, administrator connection and restart passed.')
 finally:
  subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
  p.wait()
