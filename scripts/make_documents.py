"""Regenerate only the screenshot PDF and HTML gallery. Never modifies the edited report.
Requires Pillow and reportlab. Report body updates use scripts/update_report.py.
"""
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
import html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submission'; OUT.mkdir(exist_ok=True)
shots=[
 ('01-dashboard.jpg','Workspace overview','Seeded totals, seven-day revenue and the next event in the organizer workspace.'),
 ('02-events.jpg','Event catalog','Event cards display schedule, venue, price, available capacity and category filters.'),
 ('03-seat-selection.jpg','Interactive seating chart','Seats C5 and C6 are selected for a sample guest. The server price produces a total of INR 2,998.'),
 ('04-booking-confirmation.jpg','Confirmed booking ticket','The API has saved the booking and returned its reference, amount and assigned seats.'),
 ('05-check-in.jpg','Guest check in','The confirmed sample booking has been marked checked in. Cancellation is no longer available.'),
 ('06-bookings.jpg','Searchable booking history','The guest list is filtered to the sample guest and shows the checked-in status.'),
 ('07-venues.jpg','Venue management','Three seeded venues show their rectangular seat capacity and scheduled event counts.'),
 ('08-create-venue.jpg','New venue form','Campus Auditorium is configured with 6 rows and 10 seats per row, for 60 seats.'),
 ('09-create-event.jpg','New event form','Campus Innovate 2026 is linked to the new venue with a future date and INR 799 ticket price.'),
 ('10-cancellation.jpg','Booking cancellation','The organizer reviews the affected seats and confirmed revenue before cancelling a seeded booking.'),
 ('11-sales-analytics.jpg','Sales analytics overview','Current revenue and occupancy after a booking, a cancellation and a new event.'),
 ('12-event-performance.jpg','Event performance table','Confirmed ticket counts, occupancy and revenue are compared across individual events.'),
 ('13-mobile-overview.jpg','Responsive mobile overview','The organizer workspace adapts to a 390 by 844 mobile viewport with horizontal navigation.')]
if (ROOT/'screenshots/14-docker-application.jpg').exists():shots.append(('14-docker-application.jpg','Earlier Docker application output','Historical PostgreSQL demonstration on localhost port 4301. The later Oracle output verifies the registered P_014 database stack.'))
if (ROOT/'screenshots/15-oracle-application.jpg').exists():shots.append(('15-oracle-application.jpg','Oracle database application output','The updated P_014 application runs with Angular, Spring Boot and Oracle Database Free. Java Batch 4 project configuration.'))
c=canvas.Canvas(str(OUT/'VenueVista-Output-Screenshots.pdf'),pagesize=landscape(letter));W,H=landscape(letter)
c.setTitle('VenueVista application output screenshots');c.setAuthor('')
for idx,(file,title,caption) in enumerate(shots,1):
    c.setFillColorRGB(0,0,0);c.setFont('Helvetica-Bold',17);c.drawString(35,H-36,'VenueVista '+title)
    c.setFont('Helvetica',9.5);c.setFillColorRGB(.32,.30,.36)
    # Wrap without letting a caption cross the printable margin.
    import textwrap
    for j,line in enumerate(textwrap.wrap(caption,115)):c.drawString(35,H-54-j*13,line)
    im=Image.open(ROOT/'screenshots'/file);maxw=W-70;maxh=H-115;scale=min(maxw/im.width,maxh/im.height)
    iw,ih=im.width*scale,im.height*scale;x=(W-iw)/2;y=32+(maxh-ih)/2
    c.drawImage(ImageReader(im),x,y,width=iw,height=ih)
    c.setFont('Helvetica',8);c.setFillColorRGB(.45,.4,.5);c.drawString(35,17,'Actual application output | 24 November 2026 | Fictitious demonstration data')
    c.drawRightString(W-35,17,f'{idx} / {len(shots)}');c.showPage()
c.save()
items=''.join(f'<article><h2>{html.escape(title)}</h2><p>{html.escape(caption)}</p><a href="{file}"><img src="{file}" alt="{html.escape(title)}"></a></article>' for file,title,caption in shots)
(ROOT/'screenshots/index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>VenueVista output screenshots</title><style>body{font:16px/1.6 system-ui;max-width:1100px;margin:40px auto;padding:0 24px;color:#292034;background:#f7f5fb}h1{font-size:36px}article{background:white;padding:25px;margin:25px 0;border:1px solid #e6e0ee;border-radius:10px}h2{margin-top:0}p{color:#776386}img{display:block;max-width:100%;max-height:850px;margin:auto;object-fit:contain}</style><h1>VenueVista application output</h1><p>Actual screens from the local application. The gallery records a demonstration sequence; counts change as records are created, checked in or cancelled.</p>'+items+'</html>')
print('Updated screenshot PDF and gallery with',len(shots),'screens. The edited report is unchanged.')
