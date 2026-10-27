import hashlib,io,json,os,sqlite3,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import updater
class UpdateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'app';self.root.mkdir();self.data=self.root/'data';self.data.mkdir()
  self.patches=[patch.object(updater,'ROOT',self.root),patch.object(updater,'DATA',self.data)]
  for p in self.patches:p.start()
  for name in updater.FILES:
   f=self.root/name;f.parent.mkdir(exist_ok=True,parents=True);f.write_text('0.2.0' if name=='VERSION' else '# old')
  with sqlite3.connect(self.data/'schedule.db') as c:c.execute('CREATE TABLE jobs(customer)');c.execute("INSERT INTO jobs VALUES('Keep me')")
 def tearDown(self):
  for p in self.patches:p.stop()
  self.tmp.cleanup()
 def archive(self,extra=None):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:
   for n in updater.FILES:z.writestr(n,'0.2.1' if n=='VERSION' else '# updated')
   if extra:z.writestr(extra,'bad')
  return b.getvalue()
 def stage(self):
  p=self.data/'pending-update';p.mkdir();raw=self.archive();(p/'release.zip').write_bytes(raw);(p/'manifest.json').write_text(json.dumps({'version':'0.2.1','sha256':hashlib.sha256(raw).hexdigest()}))
 def test_validation(self):
  self.assertEqual(updater.version('v0.10.0'),(0,10,0))
  for val in ['../bad','0.2','v1.2.3-beta']:
   with self.assertRaises(ValueError):updater.version(val)
  with self.assertRaises(ValueError):updater.configure('https://example.com/test')
  with self.assertRaises(ValueError):updater.inspect(self.archive('../outside'),'0.2.1')
  with self.assertRaises(ValueError):updater.inspect(self.archive('data/schedule.db'),'0.2.1')
  with self.assertRaises(ValueError):updater.inspect(self.archive(),'0.2.2')
 def test_install_preserves_data(self):
  self.stage();backup=updater.apply();self.assertEqual(updater.current(),'0.2.1')
  for db in [self.data/'schedule.db',backup/'schedule.db']:
   with sqlite3.connect(db) as c:self.assertEqual(c.execute('SELECT customer FROM jobs').fetchone()[0],'Keep me')
  self.assertFalse((self.data/'pending-update').exists());updater.rollback_code(backup);self.assertEqual(updater.current(),'0.2.0')
 def test_copy_failure_restores_code(self):
  self.stage();original=os.replace;count=0
  def fail(src,dst):
   nonlocal count
   count+=1
   if count==2:raise PermissionError('simulated file lock')
   return original(src,dst)
  with patch.object(updater.os,'replace',side_effect=fail):
   with self.assertRaises(PermissionError):updater.apply()
  self.assertEqual((self.root/'server.py').read_text(),'# old');self.assertEqual(updater.current(),'0.2.0')
 def test_download_and_checksum(self):
  updater.configure('example/store');raw=self.archive();a={'name':updater.ASSET,'digest':'sha256:'+hashlib.sha256(raw).hexdigest(),'browser_download_url':'https://github.com/example/store/releases/download/v0.2.1/'+updater.ASSET}
  release={'tag_name':'v0.2.1','body':'Release notes','assets':[a]}
  with patch.object(updater,'fetch',side_effect=[json.dumps(release).encode(),raw]):updater.stage('0.2.1')
  self.assertTrue((self.data/'pending-update/manifest.json').exists())
  a['digest']='sha256:'+'0'*64
  with patch.object(updater,'fetch',side_effect=[json.dumps(release).encode(),raw]):
   with self.assertRaisesRegex(ValueError,'checksum'):updater.stage('0.2.1')
 def test_stale_release(self):
  with patch.object(updater,'check',return_value={'available':True,'latest':'0.2.2'}):
   with self.assertRaisesRegex(ValueError,'changed'):updater.stage('0.2.1')
if __name__=='__main__':unittest.main()
