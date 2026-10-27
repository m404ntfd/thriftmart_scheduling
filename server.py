"""Store Dispatch: trusted-local-network scheduling server. Python 3.11+."""
import datetime as dt
import hashlib, hmac, json, os, secrets, socket, sqlite3, threading, time
import updater
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie

ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('DISPATCH_DATA', ROOT/'data'))
DATA.mkdir(parents=True, exist_ok=True)
DB=DATA/'schedule.db'
LOCK=threading.RLock()
SESSIONS={}
ATTEMPTS={}
RESTART=False

def connect():
    c=sqlite3.connect(DB, timeout=15)
    c.row_factory=sqlite3.Row
    return c

def init():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY COLLATE NOCASE, salt TEXT, hash TEXT, admin INTEGER);
CREATE TABLE IF NOT EXISTS vehicles(name TEXT PRIMARY KEY COLLATE NOCASE);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, revision INTEGER, body TEXT);
CREATE TABLE IF NOT EXISTS audit(at TEXT, actor TEXT, action TEXT, job TEXT);''')

def password(p,s): return hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),200000).hex()
def backup():
    folder=DATA/'backups'; folder.mkdir(exist_ok=True)
    target=folder/(dt.date.today().isoformat()+'.db')
    if not target.exists():
        with connect() as src, sqlite3.connect(target) as dest: src.backup(dest)
        for old in sorted(folder.glob('*.db'))[:-30]: old.unlink()

def background():
    while True:
        try:
            with LOCK: backup()
        except Exception as e: print('Backup failed:',e)
        time.sleep(3600)

class Problem(Exception):
    def __init__(self,message,status=400): self.message=message; self.status=status

class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args): pass
    def send(self,data,status=200,cookie=None,kind='application/json'):
        raw=json.dumps(data).encode() if kind=='application/json' else data
        self.send_response(status)
        self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        if cookie: self.send_header('Set-Cookie',cookie)
        self.end_headers(); self.wfile.write(raw)
    def user(self):
        cookie=SimpleCookie(); cookie.load(self.headers.get('Cookie',''))
        token=cookie.get('session'); token=token.value if token else ''
        session=SESSIONS.get(token)
        if not session or session['expires']<time.time(): raise Problem('Please sign in again.',401)
        return session
    def do_GET(self):
        try:
            if self.path in ('/','/app.js','/style.css'):
                filename={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[self.path]
                kind={'/':'text/html; charset=utf-8','/app.js':'text/javascript','/style.css':'text/css'}[self.path]
                return self.send((ROOT/'static'/filename).read_bytes(),kind=kind)
            with LOCK, connect() as c:
                if self.path=='/api/session':
                    setup=not c.execute('SELECT 1 FROM users').fetchone()
                    try: u=self.user()
                    except Problem: u=None
                    return self.send({'version':updater.current(),'setup':setup,'user':u and {'name':u['name'],'admin':u['admin']},'local':self.client_address[0] in ('127.0.0.1','::1')})
                u=self.user()
                if self.path=='/api/updates' and u['admin']:
                    last=DATA/'last-update.json'
                    return self.send({'current':updater.current(),'repository':updater.repo(),'launcher':os.environ.get('DISPATCH_LAUNCHER')=='1','last':json.loads(last.read_text()) if last.exists() else None})
                if self.path=='/api/state':
                    return self.send({'jobs':[dict(json.loads(r['body']),id=r['id'],revision=r['revision']) for r in c.execute('SELECT * FROM jobs')], 'vehicles':[r[0] for r in c.execute('SELECT name FROM vehicles ORDER BY name')], 'users':[dict(r) for r in c.execute('SELECT name,admin FROM users ORDER BY name')]})
                if self.path=='/api/audit' and u['admin']:
                    return self.send([dict(r) for r in c.execute('SELECT * FROM audit ORDER BY rowid DESC LIMIT 100')])
                raise Problem('Not found',404)
        except Problem as e: self.send({'error':e.message},e.status)
    def do_POST(self):
        global RESTART
        try:
            if self.headers.get('X-Dispatch')!='1': raise Problem('Invalid request.',403)
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+self.headers.get('Host',''): raise Problem('Invalid origin.',403)
            n=int(self.headers.get('Content-Length','0'))
            if n>64000: raise Problem('Request too large.')
            d=json.loads(self.rfile.read(n))
            if not isinstance(d,dict): raise Problem('Invalid request.')
            with LOCK, connect() as c:
                if RESTART: raise Problem('Update is restarting the server. Please wait and sign in again.',503)
                if self.path in ('/api/setup','/api/login'):
                    name=str(d.get('name','')).strip(); p=str(d.get('password',''))
                    if self.path=='/api/setup':
                        if self.client_address[0] not in ('127.0.0.1','::1'): raise Problem('Create the first account on the server computer.',403)
                        if c.execute('SELECT 1 FROM users').fetchone(): raise Problem('Already set up.',409)
                        self.add_user(c,name,p,True)
                    key=self.client_address[0]; attempts=[t for t in ATTEMPTS.get(key,[]) if t>time.time()-300]
                    if len(attempts)>=15: raise Problem('Too many attempts. Wait five minutes.',429)
                    r=c.execute('SELECT * FROM users WHERE name=?',(name,)).fetchone()
                    if not r or not hmac.compare_digest(r['hash'],password(p,r['salt'])):
                        ATTEMPTS[key]=attempts+[time.time()]; raise Problem('Incorrect name or password.',401)
                    token=secrets.token_urlsafe(32); SESSIONS[token]={'name':r['name'],'admin':bool(r['admin']),'expires':time.time()+43200}
                    return self.send({'ok':True},cookie=f'session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200')
                u=self.user()
                if self.path=='/api/logout':
                    for k,v in list(SESSIONS.items()):
                        if v is u: del SESSIONS[k]
                    return self.send({'ok':True},cookie='session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
                if self.path.startswith('/api/update-'):
                    if not u['admin']: raise Problem('Administrator access required.',403)
                    try:
                        if self.path=='/api/update-config': updater.configure(str(d.get('repository','')).strip())
                        elif self.path=='/api/update-check':
                            result=updater.check(); result.pop('asset',None); return self.send(result)
                        elif self.path=='/api/update-install':
                            if os.environ.get('DISPATCH_LAUNCHER')!='1': raise ValueError('Restart using Start-Store-Dispatch.bat to enable installation.')
                            updater.stage(str(d.get('version','')))
                            RESTART=True
                            self.send({'ok':True,'restarting':True})
                            threading.Thread(target=self.server.shutdown,daemon=True).start()
                            return
                        else: raise Problem('Not found',404)
                    except ValueError as e: raise Problem(str(e))
                elif self.path=='/api/user':
                    if not u['admin']: raise Problem('Administrator access required.',403)
                    self.add_user(c,str(d.get('name','')).strip(),str(d.get('password','')),False)
                elif self.path=='/api/vehicle':
                    if not u['admin']: raise Problem('Administrator access required.',403)
                    name=str(d.get('name','')).strip()
                    if not 1<=len(name)<=80: raise Problem('Enter a vehicle name.')
                    c.execute('INSERT INTO vehicles VALUES(?)',(name,))
                elif self.path in ('/api/save','/api/delete'):
                    jid=str(d.get('id') or secrets.token_hex(12))
                    old=c.execute('SELECT * FROM jobs WHERE id=?',(jid,)).fetchone()
                    if d.get('id') and (not old or d.get('revision')!=old['revision']): raise Problem('Someone changed this job. Close this form, refresh, and try again.',409)
                    if self.path=='/api/delete':
                        if not old: raise Problem('Job not found.',404)
                        c.execute('DELETE FROM jobs WHERE id=?',(jid,)); action='Removed: '+json.loads(old['body'])['customer']
                    else:
                        fields=['type','customer','phone','address','items','vehicle','start','end','staff','notes','status']
                        j={k:str(d.get(k,'')).strip() for k in fields}
                        if any(len(v)>5000 for v in j.values()): raise Problem('A field is too long.')
                        if any(not j[k] for k in ('customer','address','items','vehicle','start','end')): raise Problem('Complete the required fields.')
                        if j['type'] not in ('Pickup','Delivery') or j['status'] not in ('Scheduled','Confirmed','Completed','Canceled'): raise Problem('Invalid type or status.')
                        try:
                            start=dt.datetime.strptime(j['start'],'%Y-%m-%dT%H:%M'); end=dt.datetime.strptime(j['end'],'%Y-%m-%dT%H:%M')
                        except ValueError: raise Problem('Choose a valid date and time.')
                        if end<=start: raise Problem('End time must be after start time.')
                        if not c.execute('SELECT 1 FROM vehicles WHERE name=?',(j['vehicle'],)).fetchone(): raise Problem('Choose an existing vehicle.')
                        if j['status'] not in ('Completed','Canceled'):
                            for r in c.execute('SELECT * FROM jobs WHERE id!=?',(jid,)):
                                other=json.loads(r['body'])
                                if other['vehicle']==j['vehicle'] and other['status'] not in ('Completed','Canceled') and j['start']<other['end'] and j['end']>other['start']:
                                    raise Problem('This vehicle is already booked during that time. Choose another time or vehicle.',409)
                        rev=old['revision']+1 if old else 1
                        c.execute('INSERT OR REPLACE INTO jobs VALUES(?,?,?)',(jid,rev,json.dumps(j)))
                        action=('Updated: ' if old else 'Created: ')+j['customer']
                    c.execute('INSERT INTO audit VALUES(?,?,?,?)',(dt.datetime.now().isoformat(timespec='seconds'),u['name'],action,jid))
                else: raise Problem('Not found',404)
            self.send({'ok':True})
        except Problem as e: self.send({'error':e.message},e.status)
        except sqlite3.IntegrityError: self.send({'error':'That name already exists.'},409)
        except (ValueError,TypeError): self.send({'error':'Invalid request.'},400)
        except Exception as e:
            print('Request failed:',e); self.send({'error':'Unable to save. Check the server and try again.'},500)
    def add_user(self,c,name,p,admin):
        if not 1<=len(name)<=80 or len(p)<8 or len(p)>256: raise Problem('Enter a name and a password of 8–256 characters.')
        salt=secrets.token_hex(16)
        c.execute('INSERT INTO users VALUES(?,?,?,?)',(name,salt,password(p,salt),int(admin)))

if __name__=='__main__':
    init(); threading.Thread(target=background,daemon=True).start()
    port=int(os.environ.get('DISPATCH_PORT','8080'))
    print(f'On this computer: http://localhost:{port}')
    for address in sorted(set(socket.gethostbyname_ex(socket.gethostname())[2])):
        if not address.startswith('127.'): print(f'On store Wi-Fi: http://{address}:{port}')
    print('Keep this window open. Press Ctrl+C to stop.')
    http=ThreadingHTTPServer(('0.0.0.0',port),Handler)
    http.serve_forever()
    http.server_close()
    if RESTART: raise SystemExit(75)
