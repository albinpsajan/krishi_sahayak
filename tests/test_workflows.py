"""HTTP regression tests against an isolated database and disposable local server.

Uses Python's standard library so tests do not require an additional HTTP client.
The user's working database and uploads are never changed.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
import urllib.error
import uuid
from datetime import date, timedelta


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='krishi-http-')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.base = f'http://127.0.0.1:{cls.port}/api'
        env = os.environ.copy()
        env['KRISHI_DB_PATH'] = str(Path(cls.temp.name) / 'test.db')
        env.pop('DATABASE_URL', None)
        env['PORT'] = str(cls.port)
        env['PYTHONUTF8'] = '1'
        env['KRISHI_RELOAD'] = '0'
        root = Path(__file__).resolve().parents[1]
        cls.server = subprocess.Popen([sys.executable, str(root / 'run_app.py')], cwd=root, env=env,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                code, data = cls.request('POST', '/auth/login', {'identifier':'farmer', 'password':'farmer123'})
                if code == 200:
                    cls.farmer = data['access_token']
                    break
            except OSError:
                time.sleep(.1)
        else:
            cls.server.terminate()
            raise RuntimeError('Isolated test server did not start')
        cls.officer = cls.request('POST', '/auth/login', {'identifier':'officer','password':'officer123'})[1]['access_token']
        account = {'username':'another_farmer','email':'another@example.com','password':'strong-test-password','full_name':'Another Farmer'}
        cls.other = cls.request('POST','/auth/register',account)[1]['access_token']

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=10)
        cls.temp.cleanup()

    @classmethod
    def request(cls, method, path, body=None, token=None):
        headers = {'Content-Type':'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(cls.base+path, data=json.dumps(body).encode() if body is not None else None,
                                         headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            with error:
                return error.code, json.load(error)

    def book(self, key=None, token=None, offset=5):
        return self.request('POST','/operations/bookings',{'resource_id':1,'date':str(date.today()+timedelta(days=offset)),
                 'slot':'Morning','request_key':key or str(uuid.uuid4()),'notes':'Integration test'},token or self.farmer)

    def test_authentication_required(self):
        self.assertEqual(self.request('GET','/operations/plots')[0],401)

    def test_registration_cannot_grant_officer_role(self):
        response=self.request('POST','/auth/register',{'username':'pretend_officer','email':'staff@example.com',
                              'password':'strong-test-password','role':'OFFICER'})
        self.assertEqual(response[0],403)

    def test_profile_cannot_escalate_role(self):
        self.assertEqual(self.request('PUT','/auth/details',{'full_name':'Test','age':30,'role':'OFFICER'},self.other)[0],403)

    def test_booking_retry_is_idempotent(self):
        key=str(uuid.uuid4())
        first=self.book(key)
        second=self.book(key)
        self.assertEqual(first[0],201)
        self.assertEqual(first[1]['id'],second[1]['id'])

    def test_slot_conflict_and_cancellation_release(self):
        first=self.book(offset=7)[1]['id']
        second=self.book(token=self.other,offset=7)[1]['id']
        self.assertEqual(self.request('PATCH',f'/operations/bookings/{first}',{'status':'Confirmed'},self.officer)[0],200)
        self.assertEqual(self.request('PATCH',f'/operations/bookings/{second}',{'status':'Confirmed'},self.officer)[0],409)
        self.assertEqual(self.request('PATCH',f'/operations/bookings/{first}',{'status':'Cancelled'},self.farmer)[0],200)
        self.assertEqual(self.request('PATCH',f'/operations/bookings/{second}',{'status':'Confirmed'},self.officer)[0],200)

    def test_farmer_cannot_confirm_or_cancel_another_booking(self):
        identifier=self.book()[1]['id']
        self.assertEqual(self.request('PATCH',f'/operations/bookings/{identifier}',{'status':'Confirmed'},self.farmer)[0],403)
        self.assertEqual(self.request('PATCH',f'/operations/bookings/{identifier}',{'status':'Cancelled'},self.other)[0],403)

    def test_complete_crop_report_review_close_and_reopen(self):
        status,report=self.request('POST','/cases',{'crop_type':'Paddy','field_location':'Test field',
                                    'symptoms_description':'Lower leaves turned yellow over the last three days.'},self.other)
        self.assertEqual(status,200)
        self.assertIsNone(report['ai_assessment'])
        identifier=report['id']
        self.assertEqual(self.request('GET',f'/cases/{identifier}',token=self.farmer)[0],403)
        advice={'verified_recommendation':'Arrange a field visit and take clear photographs before any treatment.', 'follow_up_days':3}
        self.assertEqual(self.request('POST',f'/cases/{identifier}/review',advice,self.farmer)[0],403)
        self.assertEqual(self.request('POST',f'/cases/{identifier}/review',advice,self.officer)[0],200)
        self.assertEqual(self.request('POST',f'/cases/{identifier}/review',advice,self.officer)[0],200)
        self.assertEqual(self.request('PATCH',f'/cases/{identifier}/status',{'status':'Closed'},self.other)[0],200)
        self.assertEqual(self.request('PATCH',f'/cases/{identifier}/status',{'status':'Awaiting Officer Review'},self.other)[0],200)

    def test_plot_and_cashbook_ownership(self):
        before=len(self.request('GET','/operations/plots',token=self.farmer)[1])
        payload={'name':'Test plot','crop':'Paddy','area':1.2,'water_source':'Canal','planting_date':str(date.today())}
        self.assertEqual(self.request('POST','/operations/plots',payload,self.other)[0],201)
        self.assertEqual(len(self.request('GET','/operations/plots',token=self.farmer)[1]),before)
        self.assertEqual(self.request('POST','/operations/cashbook',{'crop':'Paddy','category':'Seeds','kind':'Expense',
                         'amount':-1,'date':str(date.today())},self.other)[0],422)

    def test_group_join_is_unique_and_stages_are_ordered(self):
        payload={'title':'Shared harvest transport','category':'Transport','location':'Test village',
                 'date':str(date.today()+timedelta(days=10)),'description':'Agree pickup points and split transport charges.'}
        identifier=self.request('POST','/operations/groups',payload,self.other)[1]['id']
        self.request('POST',f'/operations/groups/{identifier}/join',token=self.farmer)
        self.request('POST',f'/operations/groups/{identifier}/join',token=self.farmer)
        rows=self.request('GET','/operations/groups',token=self.farmer)[1]
        self.assertEqual(next(g for g in rows if g['id']==identifier)['count'],2)
        self.assertEqual(self.request('PATCH',f'/operations/groups/{identifier}',{'status':'Completed'},self.officer)[0],409)
        self.assertEqual(self.request('PATCH',f'/operations/groups/{identifier}',{'status':'Coordinating'},self.officer)[0],200)

    def test_new_accounts_have_no_seeded_farm_or_financial_data(self):
        account={'username':'clean_farmer','email':'clean@example.com','password':'strong-test-password'}
        token=self.request('POST','/auth/register',account)[1]['access_token']
        for endpoint in ['plots','cashbook','bookings','documents']:
            self.assertEqual(self.request('GET','/operations/'+endpoint,token=token)[1],[])

    def test_private_photos_require_authentication(self):
        self.assertEqual(self.request('GET','/uploads/1/'+'0'*32+'.jpg')[0],401)
        self.assertEqual(self.request('GET','/uploads/1/'+'0'*32+'.jpg',token=self.other)[0],403)


if __name__ == '__main__':
    unittest.main()
