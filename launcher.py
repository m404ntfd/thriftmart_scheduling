"""Stable supervisor. Runs the server; installs only on an explicit admin request."""
import os, subprocess, sys, time, urllib.request, json
from pathlib import Path
import updater
ROOT=Path(__file__).resolve().parent

def start():
    return subprocess.Popen([sys.executable,str(ROOT/'server.py')],env={**os.environ,'DISPATCH_LAUNCHER':'1'})

def healthy(p):
    for _ in range(40):
        if p.poll() is not None:return False
        try:
            with urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('DISPATCH_PORT','8080')+'/api/session',timeout=1) as r:
                if json.load(r).get('version')==updater.current():return True
        except Exception:pass
        time.sleep(.25)
    return False

def main():
    p=start()
    try:
        while True:
            code=p.wait()
            if code!=75:return code
            try: backup=updater.apply()
            except Exception as e:
                print('Update was not installed:',e);p=start();continue
            p=start()
            if not healthy(p):
                print('New version failed its startup check. Restoring previous program files.')
                if p.poll() is None:p.terminate();p.wait()
                updater.rollback_code(backup);p=start()
                (updater.DATA/'last-update.json').write_text(json.dumps({'error':'New version failed to start. Previous program files restored.','backup':str(backup)}))
            # A fresh supervisor must use the newly installed updater on the next update.
            import importlib
            importlib.reload(updater)
    except KeyboardInterrupt:
        if p.poll() is None:p.terminate();p.wait()
        return 0
if __name__=='__main__':raise SystemExit(main())
