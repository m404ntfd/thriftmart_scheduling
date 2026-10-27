import http.cookiejar,json,os,socket,subprocess,sys,tempfile,time,unittest,urllib.request,urllib.error
from pathlib import Path
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory()
  with socket.socket() as s:s.bind(('127.0.0.1',0));cls.port=s.getsockname()[1]
  cls.p=subprocess.Popen([sys.executable,str(Path(__file__).with_name('server.py'))],env={**os.environ,'DISPATCH_DATA':cls.tmp.name,'DISPATCH_PORT':str(cls.port)},stdout=subprocess.DEVNULL)
  cls.client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  for i in range(100):
   try: cls.call('session');break
   except OSError: time.sleep(.05)
 @classmethod
 def tearDownClass(cls):cls.p.terminate();cls.p.wait();cls.tmp.cleanup()
 @classmethod
 def call(cls,path,data=None,client=None):
  req=urllib.request.Request(f'http://127.0.0.1:{cls.port}/api/'+path,data=json.dumps(data).encode() if data is not None else None,headers={'X-Dispatch':'1','Content-Type':'application/json'})
  try:
   with (client or cls.client).open(req) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_workflow(self):
  self.assertTrue(self.call('session')[1]['setup'])
  self.assertEqual(self.call('local/stop',{'token':'invalid'})[0],403)
  anon=urllib.request.build_opener()
  self.assertEqual(self.call('state',client=anon)[0],401)
  self.assertEqual(self.call('setup',{'name':'Manager','password':'testpassword'})[0],200)
  self.assertEqual(self.call('setup',{'name':'Other','password':'testpassword'})[0],409)
  self.assertEqual(self.call('updates')[1]['current'],Path(__file__).with_name('VERSION').read_text().strip())
  self.assertEqual(self.call('update-config',{'repository':'example/store'})[0],200)
  self.assertEqual(self.call('updates')[1]['repository'],'example/store')
  self.assertEqual(self.call('update-install',{'version':'0.2.1'})[0],400)
  self.assertEqual(self.call('vehicle',{'name':'Truck 1'})[0],200)
  self.assertEqual(self.call('user',{'name':'Alex','password':'testpassword'})[0],200)
  job=dict(type='Pickup',status='Scheduled',customer='Test customer',phone='',address='Test address',items='Sofa',vehicle='Truck 1',start='2026-10-28T09:00',end='2026-10-28T10:00',staff='',notes='')
  self.assertEqual(self.call('save',job)[0],200)
  self.assertEqual(self.call('save',job)[0],409)
  saved=self.call('state')[1]['jobs'][0]
  self.assertEqual(self.call('save',{**saved,'notes':'Changed'})[0],200)
  self.assertEqual(self.call('save',saved)[0],409)
  self.assertEqual(self.call('delete',saved)[0],409)
  self.assertEqual(self.call('save',{**job,'start':'2026-10-28T10:00','end':'2026-10-28T11:00'})[0],200)
  employee=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  self.assertEqual(self.call('login',{'name':'Alex','password':'testpassword'},employee)[0],200)
  self.assertEqual(self.call('vehicle',{'name':'Truck 2'},employee)[0],403)
  self.assertEqual(self.call('update-config',{'repository':'other/repo'},employee)[0],403)
  self.assertEqual(self.call('update-install',{'version':'0.2.1'},employee)[0],403)
  fresh=self.call('state',client=employee)[1]['jobs'][0]
  self.assertEqual(self.call('save',{**fresh,'status':'Canceled'},employee)[0],200)
  self.assertEqual(self.call('save',job,employee)[0],200)
  fresh=self.call('state')[1]['jobs'][0]
  self.assertEqual(self.call('delete',fresh,employee)[0],200)
  self.assertTrue(len(self.call('audit')[1])>=5)
  self.assertEqual(self.call('save',{**job,'end':'2026-10-27T09:00'})[0],400)
  self.assertEqual(self.call('logout',{})[0],200)
  self.assertEqual(self.call('state')[0],401)
if __name__=='__main__':unittest.main()
