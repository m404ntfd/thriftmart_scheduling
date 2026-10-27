'use strict';
const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let state={jobs:[],vehicles:[],users:[]},user,setup=false,mode='day',editing=null,timer;
const localDate=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
$('date').value=localDate(new Date());
$('mobileLink').href=location.origin+'/mobile';$('mobileLink').textContent=location.origin+'/mobile';
async function api(path,data){const r=await fetch('/api/'+path,{method:data?'POST':'GET',headers:data?{'Content-Type':'application/json','X-Dispatch':'1'}:{},body:data?JSON.stringify(data):undefined});const v=await r.json();if(!r.ok){if(r.status===401&&user){user=null;clearInterval(timer);$('app').hidden=true;$('auth').hidden=false;$('editor').close();$('passwordDialog').close();$('statusDialog').close();}throw Error(v.error||'Request failed');}return v;}
function toast(s){$('toast').textContent=s;$('toast').hidden=false;setTimeout(()=>$('toast').hidden=true,5000);}
async function boot(){try{const s=await api('session');setup=s.setup;user=s.user;$('authTitle').textContent=setup?'Set up your store':'Welcome back';$('authHelp').textContent=setup?(s.local?'Create the administrator account. Then add your vehicles and employees.':'Open http://localhost:8080 on the server computer to create the first account.'):'Sign in to the shared store schedule.';$('auth').hidden=!!user;$('app').hidden=!user;$('connection').textContent=user?'Connected to store':'Store server online';if(user){$('settingsTab').hidden=!user.admin;$('serverUpdateButton').hidden=!user.admin;if(!user.admin)tab('day');await refresh();clearInterval(timer);timer=setInterval(()=>refresh().catch(()=>{}),10000);}}catch(e){$('connection').textContent='Server unavailable';$('offline').hidden=false;toast(e.message);}}
async function refresh(){try{state=await api('state');user.can_create=state.permissions.can_create;user.see_requests=state.permissions.see_requests;renderRequests();$('connection').textContent='● Connected · '+new Date().toLocaleTimeString([],{hour:'numeric',minute:'2-digit'});$('offline').hidden=true;const value=$('filter').value;$('filter').innerHTML='<option value="">All vehicles</option>'+state.vehicles.map(v=>`<option>${esc(v)}</option>`).join('');$('filter').value=value;render();$('vehicles').innerHTML=state.vehicles.map(v=>`<div class="listRow">${esc(v)}</div>`).join('')||'<p>No vehicles yet.</p>';$('users').innerHTML=state.users.map(v=>`<div class="listRow">${esc(v.name)}${v.admin?' · Administrator':''} <button type="button" data-password="${esc(v.name)}">Change password</button></div>`).join('');}catch(e){$('connection').textContent='Disconnected';$('offline').hidden=false;throw e;}}
function filtered(){const q=$('search').value.toLowerCase();return state.jobs.filter(j=>(!$('statusFilter').value||j.status===$('statusFilter').value)&&(!$('filter').value||j.vehicle===$('filter').value)&&(!q||Object.values(j).join(' ').toLowerCase().includes(q)));}
function timeLabel(s){return new Date(s).toLocaleTimeString([],{hour:'numeric',minute:'2-digit'});}
function shiftDate(date,days){const d=new Date(date+'T12:00');d.setDate(d.getDate()+days);return localDate(d);}
function weekStart(date){return shiftDate(date,-new Date(date+'T12:00').getDay());}
function dateLabel(date){return new Date(date+'T12:00').toLocaleDateString([],{weekday:'long',month:'short',day:'numeric',year:'numeric'});}
function renderTotals(){
 const today=localDate(new Date()),tomorrow=shiftDate(today,1),start=weekStart(today);
 $('totals').innerHTML=[['Today',today,today],['Tomorrow',tomorrow,tomorrow],['This week',start,shiftDate(start,6)]].map(([label,from,to])=>{
 const jobs=state.jobs.filter(j=>j.status!=='Canceled'&&j.start.slice(0,10)>=from&&j.start.slice(0,10)<=to);
 return `<article class="totalCard"><h2>${label}</h2><p class="totalDates">${esc(dateLabel(from))}${from===to?'':' – '+esc(dateLabel(to))}</p><div class="totalNumbers"><span><strong>${jobs.filter(j=>j.type==='Pickup').length}</strong> Pickups</span><span><strong>${jobs.filter(j=>j.type==='Delivery').length}</strong> Deliveries</span></div></article>`;
 }).join('');
}
// Use directions links rather than a location search. The OS/browser controls app handoff.
function navigationUrl(address,ua=navigator.userAgent,platform=navigator.platform,touch=navigator.maxTouchPoints){
 const destination=encodeURIComponent(address);
 const apple=/iPhone|iPad|iPod/i.test(ua)||(platform==='MacIntel'&&touch>1);
 return apple?`https://maps.apple.com/?daddr=${destination}&dirflg=d`:`https://www.google.com/maps/dir/?api=1&destination=${destination}&travelmode=driving&dir_action=navigate`;
}
function smsUrl(j,ua=navigator.userAgent,platform=navigator.platform,touch=navigator.maxTouchPoints){
 const number=String(j.phone||'').replace(/[^+0-9]/g,'');
 const message=`Hi ${j.customer}, this is Thrift Mart. Our team is on the way for your scheduled ${j.type.toLowerCase()}. Please let us know if anything has changed. Thank you!`;
 const apple=/iPhone|iPad|iPod/i.test(ua)||(platform==='MacIntel'&&touch>1);
 return `sms:${number}${apple?'&':'?'}body=${encodeURIComponent(message)}`;
}
function jobCard(j){return `<article class="job status-${j.status==='In Route / In Progress'?'in-progress':esc(j.status.toLowerCase())}"><div class="appointmentType ${j.type==='Delivery'?'typeDelivery':'typePickup'}"><span aria-hidden="true">${j.type==='Delivery'?'📦 ←':'→ 🏬'}</span> ${j.type==='Delivery'?'DELIVERY':'PICKUP'}</div><button class="editIcon" data-edit="${esc(j.id)}" aria-label="Edit appointment for ${esc(j.customer)}" title="Edit appointment">✎</button><div class="time">${esc(timeLabel(j.start))}<div class="muted">to ${esc(timeLabel(j.end))}${j.end.slice(0,10)!==j.start.slice(0,10)?' · '+esc(j.end.slice(0,10)):''}</div></div><div><span class="tag">${esc(j.request?'Request':j.status)}</span><h2>${esc(j.customer)}</h2><p>${esc(j.items)}</p><p>${esc(j.address)}</p><div class="contactActions"><a target="_blank" rel="noopener noreferrer" href="${esc(navigationUrl(j.address))}" aria-label="Navigate to ${esc(j.address)}">Navigate ↗</a>${j.phone?`<a href="tel:${esc(j.phone.replace(/[^+0-9*#,;]/g,''))}">Call ${esc(j.phone)}</a><a class="textCustomer" href="${esc(smsUrl(j))}" aria-label="Text ${esc(j.customer)} that staff are on the way">Text: On Our Way</a>`:''}</div><p class="meta">${esc(j.vehicle)}${j.staff?' · '+esc(j.staff):''}</p>${j.notes?`<p class="muted">${esc(j.notes)}</p>`:''}</div><button class="statusUpdate" data-status="${esc(j.id)}">Status Update</button><div class="statusHistory">${j.statusUpdatedBy&&j.statusUpdatedAt?`Last updated by ‘<strong><em>${esc(j.statusUpdatedBy)}</em></strong>’ at ‘<strong><em>${esc(new Date(j.statusUpdatedAt).toLocaleString([],{month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'}))}</em></strong>’`:'Status update details unavailable for this older appointment.'}</div></article>`;}
function render(){
 renderTotals();
 const day=$('date').value,today=localDate(new Date()),weekly=mode==='week';
 const from=weekly?weekStart(day):day,to=weekly?shiftDate(from,6):day;
 const jobs=filtered().filter(j=>j.start.slice(0,10)<=to&&j.end.slice(0,10)>=from).sort((a,b)=>a.start.localeCompare(b.start));
 if(user&&!user.can_create)setTimeout(()=>document.querySelectorAll('#jobs .editIcon,#jobs .statusUpdate').forEach(b=>b.hidden=true),0);$('summary').textContent=`${dateLabel(from)}${weekly?' – '+dateLabel(to):''} · ${jobs.length} appointment${jobs.length===1?'':'s'}`;
 if(weekly){let html='';for(let i=0;i<7;i++){const date=shiftDate(from,i),daily=jobs.filter(j=>j.start.slice(0,10)<=date&&j.end.slice(0,10)>=date);html+=`<section class="weekDay"><h2>${esc(dateLabel(date))}</h2>${daily.map(jobCard).join('')||'<p class="dayEmpty">No appointments.</p>'}</section>`;}$('jobs').innerHTML=html;}
 else $('jobs').innerHTML=jobs.map(jobCard).join('')||'<div class="empty"><h2>No appointments to show.</h2><p>Choose another date or filter, or add a pickup or delivery.</p></div>';
 for(const [id,selected]of [['dayTab',mode==='day'&&day===today],['weekTab',weekly&&from===weekStart(today)],['nextWeekTab',weekly&&from===shiftDate(weekStart(today),7)],['settingsTab',mode==='settings']]){$(id).classList.toggle('selected',selected);$(id).setAttribute('aria-pressed',String(selected));}
 $('prev').setAttribute('aria-label',weekly?'Previous week':'Previous day');$('next').setAttribute('aria-label',weekly?'Next week':'Next day');
}
function tab(t){mode=t;if(t==='settings'){loadUpdates();loadBackups();}$('schedule').hidden=t==='settings';$('settings').hidden=t!=='settings';render();}
function quickView(offset){const today=localDate(new Date());$('date').value=offset===null?today:shiftDate(weekStart(today),offset);tab(offset===null?'day':'week');}
function openJob(id,type){if(!state.vehicles.length){toast('Add a vehicle in Settings first.');if(user.admin)tab('settings');return;}editing=id?state.jobs.find(j=>j.id===id):null;$('jobForm').reset();$('jobVehicle').innerHTML=state.vehicles.map(v=>`<option>${esc(v)}</option>`).join('');const j=editing||{state:'MS',type:type||'Pickup',status:'Scheduled',start:$('date').value+'T09:00',end:$('date').value+'T10:00'};for(const [k,v]of Object.entries(j))if($('jobForm').elements[k])$('jobForm').elements[k].value=v;
$('jobForm').elements.street.value=j.street||j.address||'';$('legacyAddress').hidden=!editing||!!j.street;
const assigned=j.staffNames|| (j.staff?[j.staff]:[]);const names=[...new Set([...state.users.map(u=>u.name),...assigned])];$('employeeOptions').innerHTML=names.map(n=>`<label><input type="checkbox" name="staffNames" value="${esc(n)}" ${assigned.includes(n)?'checked':''}> ${esc(n)}${state.users.some(u=>u.name===n)?'':' (previous assignment)'}</label>`).join('');$('employeeDropdown').open=false;employeeSummary();$('editTitle').textContent=editing?(editing.request?'Review request':'Appointment details'):(user.can_create?'New appointment':'Submit appointment request');$('save').textContent=editing?.request?'Approve & schedule':user.can_create?'Save appointment':'Submit request';$('remove').hidden=!editing;$('formError').textContent='';$('editor').showModal();}
$('login').onsubmit=async e=>{e.preventDefault();try{const wasSetup=setup;await api(setup?'setup':'login',Object.fromEntries(new FormData(e.target)));e.target.reset();await boot();if(wasSetup){tab('settings');settingsSection(3);}}catch(err){$('authError').textContent=err.message;}};
$('logout').onclick=async()=>{try{await api('logout',{});clearInterval(timer);await boot();}catch(e){toast(e.message);}};
$('dayTab').onclick=()=>quickView(null);$('weekTab').onclick=()=>quickView(0);$('nextWeekTab').onclick=()=>quickView(7);$('settingsTab').onclick=()=>tab('settings');$('addPickup').onclick=()=>openJob(null,'Pickup');$('addDelivery').onclick=()=>openJob(null,'Delivery');$('close').onclick=()=>$('editor').close();$('date').onchange=()=>{if(!$('date').value)$('date').value=localDate(new Date());tab('day');};$('filter').onchange=render;$('statusFilter').onchange=render;$('search').oninput=render;
for(const [id,step]of [['prev',-1],['next',1]])$(id).onclick=()=>{$('date').value=shiftDate($('date').value,step*(mode==='week'?7:1));render();};
$('jobs').onclick=e=>{const b=e.target.closest('[data-edit]');if(b&&user.can_create)openJob(b.dataset.edit);const status=e.target.closest('[data-status]');if(status)openStatus(status.dataset.status);};
$('jobForm').onsubmit=async e=>{e.preventDefault();$('save').disabled=true;try{await api('save',{...Object.fromEntries(new FormData(e.target)),staffNames:new FormData(e.target).getAll('staffNames'),...(editing?{id:editing.id,revision:editing.revision}:{})});$('editor').close();toast('Appointment saved.');await refresh().catch(()=>toast('Saved. Reconnect to refresh the schedule.'));}catch(err){$('formError').textContent=err.message;}finally{$('save').disabled=false;}};
$('remove').onclick=async()=>{if(!editing||!confirm('Remove this appointment from the schedule? Use Canceled status instead if you want to keep its details.'))return;try{await api('delete',{id:editing.id,revision:editing.revision});$('editor').close();toast('Appointment removed.');await refresh().catch(()=>toast('Removed. Reconnect to refresh the schedule.'));}catch(e){$('formError').textContent=e.message;}};
for(const [id,path]of [['vehicleForm','vehicle'],['userForm','user']])$(id).onsubmit=async e=>{e.preventDefault();try{await api(path,Object.fromEntries(new FormData(e.target)));e.target.reset();await refresh();toast(path==='user'?'Employee account added.':'Vehicle added.');}catch(err){toast(err.message);}};
$('auditButton').onclick=async()=>{try{const a=await api('audit');$('audit').innerHTML=a.map(r=>`<div class="listRow">${esc(r.action)}<div class="muted">${esc(r.actor)} · ${esc(r.at.replace('T',' '))}</div></div>`).join('')||'<p>No changes yet.</p>';}catch(e){toast(e.message);}};
boot();

let updateVersion=null,updateBusy=false;
async function loadUpdates(){try{const r=await api('updates');$('updateVersion').textContent='Installed version: '+r.current;$('updateRepo').value=r.repository;$('lastUpdate').textContent=r.last?(r.last.error||'Last installed: '+r.last.version+' · '+r.last.at):'';if(!r.launcher)$('updateStatus').textContent='Use Start-Store-Dispatch.bat on the server to enable update installation.';}catch(e){toast(e.message);}}
$('updateConfig').onsubmit=async e=>{e.preventDefault();if(updateBusy)return;try{await api('update-config',{repository:$('updateRepo').value});updateVersion=null;$('installUpdate').hidden=true;$('releaseNotes').textContent='';$('updateStatus').textContent='Repository saved. Ready to check.';}catch(err){$('updateStatus').textContent=err.message;}};
$('checkUpdate').onclick=async()=>{if(updateBusy)return;updateBusy=true;$('checkUpdate').disabled=true;$('installUpdate').hidden=true;$('updateStatus').textContent='Checking GitHub…';try{const r=await api('update-check',{});updateVersion=r.available?r.latest:null;$('updateStatus').textContent=r.available?'Version '+r.latest+' is available.':'You are up to date (version '+r.current+').';$('releaseNotes').textContent=r.notes;$('installUpdate').hidden=!r.available;}catch(e){$('updateStatus').textContent=e.message;}finally{updateBusy=false;$('checkUpdate').disabled=false;}};
$('installUpdate').onclick=async()=>{if(updateBusy||!updateVersion)return;if(!confirm('Install version '+updateVersion+' and restart? Ask everyone to finish saving appointments first. All users will be signed out.'))return;updateBusy=true;$('installUpdate').disabled=true;$('updateStatus').textContent='Downloading and verifying the update…';try{await api('update-install',{version:updateVersion});clearInterval(timer);$('updateStatus').textContent='Restarting. This page will reload when the server is ready.';let tries=0;const poll=setInterval(async()=>{tries++;try{const r=await api('session');if(!r.user){clearInterval(poll);location.reload();}}catch{}if(tries>=45){clearInterval(poll);$('updateStatus').textContent='The server has not returned yet. Check its window on the Windows computer, then reload this page.';}},2000);}catch(e){$('updateStatus').textContent=e.message;}finally{updateBusy=false;$('installUpdate').disabled=false;}};

async function loadBackups(){try{const r=await api('admin/backup-settings');$('backupFolder').value=r.config.folder;$('backupEnabled').checked=r.config.enabled;const s=r.status;$('backupStatus').textContent=s?(s.error?'Last backup error: '+s.error:'Last saved: '+s.at+' · '+s.file):'No complete backup saved yet.';}catch(e){$('backupStatus').textContent=e.message;}}
$('backupConfig').onsubmit=async e=>{e.preventDefault();try{await api('admin/backup-settings',{folder:$('backupFolder').value,enabled:$('backupEnabled').checked});$('backupStatus').textContent='Settings saved. Use Back up now to verify the destination.';}catch(err){$('backupStatus').textContent=err.message;}};
$('cloudBackup').onclick=async()=>{$('cloudBackup').disabled=true;$('backupStatus').textContent='Creating a complete backup…';try{const r=await api('admin/backup-now',{});$('backupStatus').textContent='Saved: '+r.backup+'. Confirm OneDrive has synced this file.';}catch(e){$('backupStatus').textContent=e.message;}finally{$('cloudBackup').disabled=false;}};

$('serverUpdateButton').onclick=()=>{tab('settings');settingsSection(2);$('updatePanel').scrollIntoView({behavior:'smooth',block:'start'});$('checkUpdate').click();};
$('users').onclick=e=>{const b=e.target.closest('[data-password]');if(!b)return;$('passwordForm').reset();$('passwordUser').value=b.dataset.password;$('passwordError').textContent='';const person=state.users.find(u=>u.name===b.dataset.password);$('canCreate').checked=!!person.can_create;$('seeRequests').checked=!!person.see_requests;$('canCreate').disabled=!!person.admin;$('permissionMessage').textContent='';$('passwordDialog').showModal();};
function closePassword(){$('passwordForm').reset();$('passwordDialog').close();}
$('passwordClose').onclick=closePassword;
$('passwordDialog').addEventListener('close',()=>$('passwordForm').reset());
$('passwordForm').onsubmit=async e=>{e.preventDefault();const d=Object.fromEntries(new FormData(e.target));if(d.password!==d.confirm){$('passwordError').textContent='The passwords do not match.';return;}$('passwordSave').disabled=true;try{const r=await api('admin/password',d);closePassword();if(r.signed_out){clearInterval(timer);await boot();toast('Password changed. Sign in with your new password.');}else toast('Password changed. The user must sign in again.');}catch(err){$('passwordError').textContent=err.message;}finally{$('passwordSave').disabled=false;}};

async function retryConnection(){if(user)await refresh().catch(()=>toast('Cannot reach the server. Check the store Wi-Fi or VPN.'));else await boot();}
$('refresh').onclick=retryConnection;$('retry').onclick=retryConnection;
window.addEventListener('online',retryConnection);
window.addEventListener('offline',()=>{$('offline').hidden=false;$('connection').textContent='Disconnected';});
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&user)retryConnection();});

function employeeSummary(){const selected=[...$('employeeOptions').querySelectorAll('input:checked')].map(e=>e.value);$('employeeSummary').textContent=selected.length?selected.join(', '):'Select employees (optional)';}
$('employeeOptions').onchange=employeeSummary;

let statusEditing=null;
function openStatus(id){
 statusEditing=state.jobs.find(j=>j.id===id);if(!statusEditing)return;
 $('statusCustomer').textContent=statusEditing.customer+' · Current status: '+statusEditing.status;
 for(const option of document.querySelectorAll('[name=appointmentStatus]'))option.checked=option.value===statusEditing.status;
 $('statusError').textContent='';$('statusDialog').showModal();
}
$('statusClose').onclick=()=>$('statusDialog').close();
$('statusForm').onsubmit=async e=>{
 e.preventDefault();if(!statusEditing)return;$('statusSave').disabled=true;
 try{await api('status',{id:statusEditing.id,revision:statusEditing.revision,status:new FormData(e.target).get('appointmentStatus')});$('statusDialog').close();toast('Status updated.');await refresh().catch(()=>toast('Status saved. Reconnect to refresh the schedule.'));}
 catch(err){$('statusError').textContent=err.message;}
 finally{$('statusSave').disabled=false;}
};

$('accountButton').onclick=()=>{$('accountForm').reset();$('accountError').textContent='';$('accountDialog').showModal();};
$('accountClose').onclick=()=>$('accountDialog').close();
$('accountForm').onsubmit=async e=>{e.preventDefault();const button=e.target.querySelector('button.primary');button.disabled=true;try{await api('account/password',Object.fromEntries(new FormData(e.target)));$('accountDialog').close();e.target.reset();await boot();toast('Login updated. Sign in with your new password or passcode.');}catch(err){$('accountError').textContent=err.message;}finally{button.disabled=false;}};

function renderRequests(){
 const requests=state.requests||[];$('requestsButton').hidden=!user.see_requests||!requests.length;$('requestsButton').textContent=`Requests (${requests.length})`;
 if(!user.see_requests)$('requestsList').hidden=true;
 $('requestsList').innerHTML=requests.map(j=>`<div class="panel"><strong>${esc(j.type)} request: ${esc(j.customer)}</strong><p>${esc(j.start)} · ${esc(j.address)} · ${esc(j.items)}</p><p>Submitted by ${esc(j.requestedBy)}</p><button data-review="${esc(j.id)}">Review request</button></div>`).join('');
 document.querySelectorAll('#jobs .editIcon,#jobs .statusUpdate').forEach(b=>b.hidden=!user.can_create);
}
$('requestsButton').onclick=()=>$('requestsList').hidden=!$('requestsList').hidden;
$('requestsList').onclick=e=>{const b=e.target.closest('[data-review]');if(!b)return;const request=state.requests.find(j=>j.id===b.dataset.review);state.jobs.push(request);openJob(request.id);};
$('savePermissions').onclick=async()=>{try{await api('admin/permissions',{name:$('passwordUser').value,can_create:$('canCreate').checked,see_requests:$('seeRequests').checked});$('permissionMessage').textContent='Permissions saved.';await refresh();}catch(e){$('permissionMessage').textContent=e.message;}};

const settingsPanels=[...$('settings').children];
const settingsTabs=document.createElement('nav');settingsTabs.className='settingsTabs';settingsTabs.setAttribute('aria-label','Settings sections');
const settingsNames=['Phone Access','Backups','Updates','Vehicles','Employees','Recent Changes'];
function settingsSection(index){settingsPanels.forEach((panel,i)=>panel.hidden=i!==index);[...settingsTabs.children].forEach((button,i)=>{button.classList.toggle('selected',i===index);button.setAttribute('aria-pressed',String(i===index));});}
settingsPanels.forEach((panel,i)=>{const button=document.createElement('button');button.type='button';button.textContent=settingsNames[i];button.onclick=()=>settingsSection(i);settingsTabs.append(button);});
$('settings').prepend(settingsTabs);settingsSection(0);
