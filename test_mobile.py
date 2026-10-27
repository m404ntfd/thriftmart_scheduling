"""Real browser tests of the shared phone schedule (run with Playwright installed)."""
import os, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def run():
    with tempfile.TemporaryDirectory() as data, socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        sock.close()
        base = f'http://127.0.0.1:{port}'
        proc = subprocess.Popen([sys.executable, 'server.py'], env={**os.environ, 'DISPATCH_DATA': data, 'DISPATCH_PORT': str(port)}, stdout=subprocess.DEVNULL)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(base + '/api/session').close()
                    break
                except OSError:
                    time.sleep(.1)
            with sync_playwright() as p:
                browser = p.chromium.launch()
                phone = browser.new_context(viewport={'width':375,'height':812}, is_mobile=True, has_touch=True)
                page = phone.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(base + '/mobile/')
                page.locator('#login [name=name]').fill('Manager')
                page.locator('#login [name=password]').fill('testpassword')
                page.locator('#login button').click()
                page.locator('#vehicleForm input').fill('White truck')
                page.locator('#vehicleForm button').click()
                expect(page.locator('#vehicles')).to_contain_text('White truck')
                page.get_by_role('button',name='Employees',exact=True).click()
                page.locator('#userForm [name=name]').fill('Alex')
                page.locator('#userForm [name=password]').fill('testpassword')
                page.locator('#userForm button').click()
                expect(page.locator('#users')).to_contain_text('Alex')
                page.locator('#dayTab').click()
                assert page.evaluate("weekStart('2026-10-31')") == '2026-10-25'
                assert page.evaluate("weekStart('2026-11-01')") == '2026-11-01'
                assert page.evaluate("shiftDate(weekStart('2026-12-31'),7)") == '2027-01-03'
                page.locator('#addDelivery').click()
                expect(page.locator('#jobForm [name=type]')).to_have_value('Delivery')
                expect(page.locator('#jobForm [name=status]')).to_have_value('Scheduled')
                expect(page.locator('#jobForm [name=state]')).to_have_value('MS')
                expect(page.locator('#jobForm [name=state] option:checked')).to_have_text('Mississippi')
                for name, value in {'customer':'Phone customer','phone':'555-0100','street':'123 Main Street','city':'Springfield','state':'IL','zip':'62701','items':'Sofa and two chairs'}.items():
                    page.locator(f'#jobForm [name={name}]').select_option(value) if name=='state' else page.locator(f'#jobForm [name={name}]').fill(value)
                page.locator('#employeeSummary').click()
                page.locator('#employeeOptions input[value=Alex]').check()
                page.locator('#employeeOptions input[value=Manager]').check()
                page.locator('#save').click()
                expect(page.locator('#jobs')).to_contain_text('Phone customer')
                expect(page.locator('#jobs .typeDelivery')).to_contain_text('DELIVERY')
                expect(page.locator('#jobs')).to_contain_text('Alex')
                expect(page.locator('#jobs')).to_contain_text('Manager')
                expect(page.locator('#jobs a[href^="tel:"]')).to_have_attribute('href','tel:5550100')
                expect(page.locator('.textCustomer')).to_have_attribute('href',page.evaluate("smsUrl(state.jobs[0])"))
                assert 'scheduled delivery' in page.evaluate("decodeURIComponent(smsUrl(state.jobs[0]))")
                assert page.evaluate("smsUrl({phone:'555-0100',customer:'Alex',type:'Pickup'},'iPhone','iPhone',1)").startswith('sms:5550100&body=')
                expect(page.locator('#jobs a[href^="https:"]')).to_have_attribute('href','https://www.google.com/maps/dir/?api=1&destination=123%20Main%20Street%0ASpringfield%2C%20IL%2062701&travelmode=driving&dir_action=navigate')
                expect(page.locator('#jobs a[href^="https:"]')).to_have_text('Navigate ↗')
                assert page.evaluate("navigationUrl('123 Main & Oak', 'iPhone', 'iPhone', 1)") == 'https://maps.apple.com/?daddr=123%20Main%20%26%20Oak&dirflg=d'
                assert page.evaluate("navigationUrl('123 Main', 'Macintosh', 'MacIntel', 5)").startswith('https://maps.apple.com/')
                assert page.evaluate("navigationUrl('123 Main', 'Android', 'Linux', 1)").endswith('travelmode=driving&dir_action=navigate')
                page.locator('[data-status]').click()
                expect(page.locator('[name=appointmentStatus]')).to_have_count(4)
                expect(page.locator('[name=appointmentStatus][value=Scheduled]')).to_be_checked()
                page.locator('.statusOptions span').get_by_text('In Route / In Progress',exact=True).click()
                page.locator('#statusSave').click()
                expect(page.locator('#jobs .status-in-progress')).to_have_count(1)
                expect(page.locator('.statusHistory')).to_contain_text('Last updated by')
                expect(page.locator('.statusHistory strong em').first).to_have_text('Manager')
                page.locator('[data-status]').click()
                page.locator('.statusOptions span').get_by_text('Completed',exact=True).click()
                page.locator('#statusSave').click()
                expect(page.locator('#jobs .status-completed')).to_have_count(1)
                page.locator('[data-status]').click()
                page.locator('.statusOptions span').get_by_text('Scheduled',exact=True).click()
                page.locator('#statusSave').click()
                expect(page.locator('#jobs .status-scheduled')).to_have_count(1)
                for width in [320,375,430,1280]:
                    page.set_viewport_size({'width':width,'height':812})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}px'
                page.set_viewport_size({'width':375,'height':812})
                page.locator('#statusFilter').select_option('Completed')
                expect(page.locator('#jobs .job')).to_have_count(0)
                page.locator('#statusFilter').select_option('')
                page.locator('#weekTab').click()
                expect(page.locator('.weekDay')).to_have_count(7)
                expect(page.locator('.weekDay h2').first).to_contain_text('Sunday')
                expect(page.locator('.weekDay h2').last).to_contain_text('Saturday')
                expect(page.locator('#jobs')).to_contain_text('Phone customer')
                page.locator('#nextWeekTab').click()
                expect(page.locator('#jobs .job')).to_have_count(0)
                expect(page.locator('#totals .totalCard').first).to_contain_text('1 Deliveries')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                page.locator('#dayTab').click()
                # A separately signed-in employee sees the same data and can edit it.
                other = browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
                employee = other.new_page()
                employee.goto(base + '/mobile')
                employee.locator('#login [name=name]').fill('Alex')
                employee.locator('#login [name=password]').fill('testpassword')
                employee.locator('#login button').click()
                expect(employee.locator('#jobs')).to_contain_text('Phone customer')
                expect(employee.locator('#settingsTab')).to_be_hidden()
                employee.locator('[data-edit]').click()
                employee.locator('#jobForm [name=notes]').fill('Call before arrival')
                employee.locator('#save').click()
                expect(employee.locator('#editor')).not_to_be_visible()
                page.locator('#refresh').click()
                expect(page.locator('#jobs')).to_contain_text('Call before arrival')
                phone.set_offline(True)
                page.locator('#refresh').click()
                expect(page.locator('#offline')).to_be_visible()
                phone.set_offline(False)
                page.locator('#refresh').click()
                expect(page.locator('#offline')).to_be_hidden()
                page.locator('[data-edit]').click()
                page.on('dialog', lambda dialog: dialog.accept())
                page.locator('#remove').click()
                expect(page.locator('#jobs .job')).to_have_count(0)
                assert not errors, errors
                browser.close()
        finally:
            proc.terminate()
            proc.wait(timeout=10)
    print('Phone CRUD, sharing, links, filters, layouts, roles and reconnection passed.')

if __name__ == '__main__':
    run()
