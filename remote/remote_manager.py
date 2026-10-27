"""Thrift Mart Dispatch Remote Manager — native Windows control panel."""
import json,os,queue,sys,threading,webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk,messagebox
from client import Client
NAME='Thrift Mart Dispatch Remote Manager'
VERSION='0.5.0'
CONFIG=Path(os.environ.get('APPDATA',Path.home()))/'ThriftMartDispatchRemoteManager'/'config.json'

class App:
    def __init__(self,root,local=False):
        self.root=root;self.client=None;self.release=None;self.busy=False;self.results=queue.Queue()
        root.title('Thrift Mart Dispatch Server — Administration' if local else NAME);root.geometry('800x830');root.minsize(720,760)
        style=ttk.Style();style.theme_use('clam');style.configure('TButton',padding=9);style.configure('TLabel',font=('Segoe UI',10));style.configure('Title.TLabel',font=('Segoe UI',22,'bold'));style.configure('TEntry',padding=7)
        frame=ttk.Frame(root,padding=24);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Thrift Mart Dispatch',style='Title.TLabel').pack(anchor='w')
        ttk.Label(frame,text=('Server administration' if local else 'Remote Manager')+' • '+VERSION+'  |  Staff network').pack(anchor='w',pady=(2,16))
        box=ttk.LabelFrame(frame,text='Connect to your store server',padding=12);box.pack(fill='x')
        try:saved=json.loads(CONFIG.read_text())
        except (OSError,ValueError):saved={}
        self.address=tk.StringVar(value='http://localhost:8080' if local else saved.get('address',''));self.username=tk.StringVar(value=saved.get('username',''));self.password=tk.StringVar()
        for label,var,secret in [('Server IP or computer name',self.address,False),('Administrator name',self.username,False),('Password',self.password,True)]:
            row=ttk.Frame(box);row.pack(fill='x',pady=3);ttk.Label(row,text=label,width=27).pack(side='left');ttk.Entry(row,textvariable=var,show='•' if secret else '').pack(side='left',fill='x',expand=True)
        ttk.Label(box,text='Example: 192.168.1.50:8080 • Passwords are never saved.').pack(anchor='w',pady=5)
        buttons=ttk.Frame(box);buttons.pack(fill='x');ttk.Button(buttons,text='Test connection',command=self.probe).pack(side='left');ttk.Button(buttons,text='Connect / Sign in',command=self.login).pack(side='left',padx=8);ttk.Button(buttons,text='Disconnect',command=self.disconnect).pack(side='left')
        self.status=tk.StringVar(value='Enter the server address shown on the store computer.')
        ttk.Label(frame,textvariable=self.status,wraplength=690).pack(fill='x',pady=12)
        self.details=tk.StringVar(value='Not connected')
        ttk.Label(frame,textvariable=self.details,wraplength=690).pack(fill='x',pady=(0,12))
        actions=ttk.Frame(frame);actions.pack(fill='x')
        ttk.Button(actions,text='Open schedule / settings',command=self.open_browser).pack(side='left')
        ttk.Button(actions,text='Refresh status',command=self.refresh).pack(side='left',padx=6)
        ttk.Button(actions,text='OneDrive backup',command=self.backup).pack(side='left')
        ttk.Button(actions,text='Restart server',command=self.restart).pack(side='left',padx=6)
        ttk.Button(frame,text='Change a user’s password',command=self.passwords).pack(anchor='w',pady=(8,0))
        updates=ttk.LabelFrame(frame,text='Server updates from GitHub',padding=12);updates.pack(fill='both',expand=True,pady=16)
        row=ttk.Frame(updates);row.pack(fill='x');ttk.Button(row,text='Check for server updates',command=self.check).pack(side='left');self.install=ttk.Button(row,text='Install update & restart',command=self.install_update,state='disabled');self.install.pack(side='left',padx=8)
        self.notes=tk.Text(updates,height=7,wrap='word',font=('Segoe UI',10),state='disabled');self.notes.pack(fill='both',expand=True,pady=8)
        ttk.Label(frame,text='Schedules, vehicles, employees and account permissions are managed in the browser.\nThe browser requires its own sign-in. Closing this app does not stop the server.',wraplength=690).pack(anchor='w')
        ttk.Button(frame,text='Remote Manager downloads / updates',command=lambda:webbrowser.open('https://github.com/m404ntfd/thriftmart_scheduling/releases/latest')).pack(anchor='w',pady=(8,0))
        root.after(100,self.deliver)
    def run(self,work,done):
        if self.busy:return
        self.busy=True;self.status.set('Working…')
        def worker():
            try:self.results.put((True,work(),done))
            except Exception as e:self.results.put((False,str(e),done))
        threading.Thread(target=worker,daemon=True).start()
    def deliver(self):
        try:
            ok,value,done=self.results.get_nowait();self.busy=False
            if ok:done(value)
            else:self.status.set(value)
        except queue.Empty:pass
        self.root.after(100,self.deliver)
    def new_client(self):return Client(self.address.get())
    def probe(self):
        if self.busy:return
        try:c=self.new_client()
        except ValueError as e:self.status.set(str(e));return
        self.run(c.probe,lambda r:self.status.set('Server is reachable • version '+r['version']))
    def login(self):
        if self.busy:return
        self.client=None;self.install.config(state='disabled');self.release=None
        try:c=self.new_client()
        except ValueError as e:self.status.set(str(e));return
        name=self.username.get().strip();password=self.password.get();self.password.set('')
        def done(r):
            self.client=c;self.show_status(r)
            try:
                CONFIG.parent.mkdir(parents=True,exist_ok=True);CONFIG.write_text(json.dumps({'address':c.address,'username':name}))
            except OSError:self.status.set('Connected, but the server address could not be saved on this computer.')
        self.run(lambda:c.login(name,password),done)
    def disconnect(self):
        if self.busy:return
        c=self.client;self.client=None;self.release=None;self.install.config(state='disabled');self.details.set('Not connected')
        if c:self.run(lambda:c.request('logout',{}),lambda _:self.status.set('Disconnected.'))
        else:self.status.set('Disconnected.')
    def require(self):
        if not self.client:self.status.set('Connect with an administrator account first.');return False
        if self.busy:return False
        return True
    def show_status(self,r):
        self.status.set('Connected to '+self.client.address)
        self.details.set(f"{r['name']} • v{r['version']}\n{r['jobs']} appointments · {r['vehicles']} vehicles · {r['users']} accounts\nUptime: {r['uptime_minutes']} minutes · Server time: {r['time']}")
    def refresh(self):
        if self.require():self.run(lambda:self.client.request('admin/status'),self.show_status)
    def open_browser(self):
        try:c=self.client or self.new_client();webbrowser.open(c.address)
        except ValueError as e:self.status.set(str(e))
    def backup(self):
        if self.require():self.run(lambda:self.client.request('admin/backup-now',{}),lambda r:self.status.set('Saved to server OneDrive folder (check sync): '+r['backup']))
    def passwords(self):
        if not self.require():return
        def show(r):
            self.status.set('Select the user whose password you want to change.')
            dialog=tk.Toplevel(self.root);dialog.title('Change user password');dialog.geometry('520x400');dialog.transient(self.root);dialog.grab_set()
            f=ttk.Frame(dialog,padding=20);f.pack(fill='both',expand=True)
            ttk.Label(f,text='Administrator password reset',font=('Segoe UI',16,'bold')).pack(anchor='w')
            ttk.Label(f,text='The selected user will be signed out on all devices.',wraplength=470).pack(anchor='w',pady=10)
            selected=tk.StringVar();first=tk.StringVar();second=tk.StringVar();error=tk.StringVar()
            ttk.Label(f,text='User').pack(anchor='w');combo=ttk.Combobox(f,textvariable=selected,values=[u['name'] for u in r['users']],state='readonly');combo.pack(fill='x',pady=4)
            if r['users']:combo.current(0)
            for label,var in [('New password',first),('Confirm new password',second)]:
                ttk.Label(f,text=label).pack(anchor='w');ttk.Entry(f,textvariable=var,show='•').pack(fill='x',pady=4)
            ttk.Label(f,textvariable=error,wraplength=470).pack(anchor='w',pady=6)
            def save():
                if not self.require():return
                if not selected.get():error.set('Select a user.');return
                if not 8<=len(first.get())<=256:error.set('Use 8–256 characters.');return
                if first.get()!=second.get():error.set('The passwords do not match.');return
                payload={'name':selected.get(),'password':first.get(),'confirm':second.get()}
                first.set('');second.set('');dialog.destroy()
                def done(result):
                    if result['signed_out']:
                        self.client=None;self.release=None;self.install.config(state='disabled');self.details.set('Sign in again with your new password.')
                    self.status.set('Password changed. The user must sign in again on all devices.')
                self.run(lambda:self.client.request('admin/password',payload),done)
            ttk.Button(f,text='Change password',command=save).pack(anchor='w')
        self.run(lambda:self.client.request('admin/users'),show)
    def restart(self):
        if not self.require():return
        if not messagebox.askyesno(NAME,'Restart the server? Ask employees to save their appointments first. Everyone will be signed out.'):return
        self.run(lambda:self.client.request('admin/restart',{}),self.restarting)
    def restarting(self,r):
        self.client=None;self.release=None;self.install.config(state='disabled');self.details.set('Server restarting')
        self.status.set('Restart requested. Wait a few seconds, then Test connection and sign in again.')
    def check(self):
        if not self.require():return
        self.install.config(state='disabled');self.release=None
        def done(r):
            self.release=r['latest'] if r['available'] else None
            self.status.set('Version '+r['latest']+' available.' if self.release else 'Server is up to date: '+r['current'])
            self.notes.config(state='normal');self.notes.delete('1.0','end');self.notes.insert('1.0',r['notes']);self.notes.config(state='disabled');self.install.config(state='normal' if self.release else 'disabled')
        self.run(lambda:self.client.request('update-check',{}),done)
    def install_update(self):
        if not self.require() or not self.release:return
        if not messagebox.askyesno(NAME,'Back up, install server version '+self.release+' and restart? Ask all employees to save their appointments first.'):return
        version=self.release;self.run(lambda:self.client.request('update-install',{'version':version}),self.restarting)

def main():
    if '--restore-self-test' in sys.argv:
        from restore import restore_self_test
        restore_self_test();return
    if '--restore-dir' in sys.argv:
        from restore import restore_window
        restore_window(Path(sys.argv[sys.argv.index('--restore-dir')+1]));return
    if '--smoke-test' in sys.argv:
        root=tk.Tk();root.withdraw();App(root);root.update();root.destroy();return
    root=tk.Tk();App(root,local='--local-server' in sys.argv);root.mainloop()
if __name__=='__main__':main()
