#!/usr/bin/env python3
"""Exercise a running VenueVista stack. Uses only the Python standard library.
Creates demonstration venue/event/booking records; does not delete existing data.
Usage: python3 scripts/smoke_test.py http://localhost:4200
"""
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

base = (sys.argv[1] if len(sys.argv)>1 else 'http://localhost:4200').rstrip('/')
results=[]
def call(method,path,payload=None,expected=200):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=20) as r: status=r.status; body=r.read()
    except urllib.error.HTTPError as ex: status=ex.code;body=ex.read()
    assert status==expected,(method,path,status,body.decode())
    return json.loads(body) if body else None
def record(name):results.append({'test':name,'status':'PASS'});print('PASS '+name)

assert call('GET','/actuator/health')['status']=='UP';record('Application health through frontend proxy')
venue=call('POST','/api/venues',{'name':'Campus Open House Hall','city':'Bengaluru','seatRows':3,'seatsPerRow':6},201)
record('Create venue in running database')
event=call('POST','/api/events',{'title':'Campus Open House','category':'Conference','venueId':venue['id'],'startsAt':(datetime.now()+timedelta(days=40)).replace(microsecond=0).isoformat(),'price':799},201)
record('Create future event')
seatmap=call('GET',f"/api/events/{event['id']}/seats")
assert seatmap=={'rows':3,'columns':6,'booked':[]};record('Read generated seating plan')
before=call('GET','/api/analytics')
payload={'eventId':event['id'],'customerName':'Demo Visitor','email':'visitor@example.com','seats':['A1','A2']}
b=call('POST','/api/bookings',payload,201)
assert b['total']==1598;record('Book two seats with server-calculated amount')
call('POST','/api/bookings',payload,409);record('Reject duplicate purchase with HTTP 409')
after=call('GET','/api/analytics');assert after['revenue']==before['revenue']+1598;assert after['ticketsSold']==before['ticketsSold']+2
record('Analytics reflect confirmed ticket sale')
call('POST',f"/api/bookings/{b['id']}/cancel",{});call('POST',f"/api/bookings/{b['id']}/cancel",{})
assert call('GET',f"/api/events/{event['id']}/seats")['booked']==[];record('Cancellation releases seats and is idempotent')
assert call('GET','/api/analytics')['revenue']==before['revenue'];record('Cancellation removes confirmed revenue')
b2=call('POST','/api/bookings',payload,201);checked=call('POST',f"/api/bookings/{b2['id']}/check-in",{})
assert checked['checkedIn'];call('POST',f"/api/bookings/{b2['id']}/cancel",{},409);record('Check-in succeeds and prevents cancellation')
call('POST','/api/venues',{'name':'Invalid Hall','city':'Pune','seatRows':0,'seatsPerRow':5},400);record('Invalid venue dimensions return HTTP 400')
record('All end-to-end API smoke checks completed')
print(json.dumps({'baseUrl':base,'verifiedAt':datetime.now().isoformat(),'bookingId':b2['id'],'reference':b2['reference'],'results':results},indent=2))
