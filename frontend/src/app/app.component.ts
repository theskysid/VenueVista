import {Component, inject, HostListener, ChangeDetectorRef} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {forkJoin} from 'rxjs';
import {Event, Venue, Booking, Analytics, SeatMap} from './models';

@Component({selector:'app-root',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./app.component.html'})
export class AppComponent {
  private http=inject(HttpClient);
  private change=inject(ChangeDetectorRef);
  page='Overview'; pages=['Overview','Events','Venues','Bookings','Analytics'];
  events:Event[]=[];venues:Venue[]=[];bookings:Booking[]=[];analytics:Analytics|null=null;
  loading=true;error='';toast='';search='';category='All events';bookingFilter='All bookings';
  modal:''|'event'|'venue'|'seats'|'ticket'|'cancel'=''; selectedEvent:Event|null=null;seatMap:SeatMap|null=null;
  selectedSeats:string[]=[];customerName='';email='';busy=false;modalError='';ticket:Booking|null=null;
  newEvent={title:'',category:'Music',venueId:0,startsAt:'',price:1499};
  newVenue={name:'',city:'',seatRows:6,seatsPerRow:10};
  categories=['Music','Conference','Theatre','Comedy','Workshop'];
  today=new Date();
  constructor(){this.load();}
  @HostListener('document:keydown.escape') escape(){if(!this.busy)this.close();}
  load(){
    this.error='';
    forkJoin({events:this.http.get<Event[]>('/api/events'),venues:this.http.get<Venue[]>('/api/venues'),bookings:this.http.get<Booking[]>('/api/bookings'),analytics:this.http.get<Analytics>('/api/analytics')})
      .subscribe({next:r=>{Object.assign(this,r);this.loading=false;this.change.markForCheck();},error:()=>{this.loading=false;this.change.markForCheck();this.error='Unable to connect to VenueVista. Start the API and try again.';}});
  }
  navigate(page:string){this.page=page;this.search='';this.category='All events';this.bookingFilter='All bookings';window.scrollTo({top:0,behavior:'instant'});}
  money(n:number){return new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(n);}
  get filteredEvents(){return this.events.filter(e=>(this.category==='All events'||e.category===this.category)&&`${e.title} ${e.venue.name} ${e.venue.city}`.toLowerCase().includes(this.search.toLowerCase()));}
  get filteredBookings(){return this.bookings.filter(b=>`${b.reference} ${b.customerName} ${b.event.title} ${b.email}`.toLowerCase().includes(this.search.toLowerCase())&&(this.bookingFilter==='All bookings'||(this.bookingFilter==='Cancelled'?b.status==='CANCELLED':this.bookingFilter==='Checked in'?b.checkedIn:b.status==='CONFIRMED'&&!b.checkedIn)));}
  get filteredVenues(){return this.venues.filter(v=>`${v.name} ${v.city}`.toLowerCase().includes(this.search.toLowerCase()));}
  get chartMax(){return Math.max(...(this.analytics?.daily.map(d=>d.revenue)||[1]),1);}
  get weeklyRevenue(){return this.analytics?.daily.reduce((sum,d)=>sum+d.revenue,0)||0;}
  get chartPoints(){return this.analytics?.daily.map((d,i)=>`${30+i*90},${160-d.revenue/this.chartMax*135}`).join(' ')||'';}
  get chartArea(){return `30,175 ${this.chartPoints} 570,175`;}
  rows(){return Array.from({length:this.seatMap?.rows||0},(_,i)=>i);}
  columns(){return Array.from({length:this.seatMap?.columns||0},(_,i)=>i+1);}
  rowName(n:number){return String.fromCharCode(65+n);}
  label(r:number,c:number){return this.rowName(r)+c;}
  openEvent(){this.modalError='';this.newEvent={title:'',category:'Music',venueId:this.venues[0]?.id||0,startsAt:'',price:1499};this.modal='event';}
  openVenue(){this.modalError='';this.newVenue={name:'',city:'',seatRows:6,seatsPerRow:10};this.modal='venue';}
  openSeats(event:Event){
    this.modalError='';this.seatMap=null;this.selectedEvent=event;this.selectedSeats=[];this.customerName='';this.email='';this.modal='seats';
    this.http.get<SeatMap>(`/api/events/${event.id}/seats`).subscribe({next:r=>{this.seatMap=r;this.change.markForCheck();},error:e=>{this.modalError=this.message(e);this.change.markForCheck();}});
  }
  toggleSeat(seat:string){if(this.selectedSeats.includes(seat))this.selectedSeats=this.selectedSeats.filter(s=>s!==seat);else if(this.selectedSeats.length<10)this.selectedSeats=[...this.selectedSeats,seat];else this.modalError='You can book up to 10 seats at a time.';}
  close(){this.modal='';this.modalError='';}
  message(e:HttpErrorResponse){return e.error?.message||'The request could not be completed. Please try again.';}
  notify(text:string){this.toast=text;this.change.markForCheck();setTimeout(()=>{this.toast='';this.change.markForCheck();},5000);}
  saveEvent(){this.busy=true;this.modalError='';this.http.post('/api/events',this.newEvent).subscribe({next:()=>{this.busy=false;this.change.markForCheck();this.close();this.load();this.notify('Your event is ready. Ticket sales are open.');},error:e=>{this.busy=false;this.change.markForCheck();this.modalError=this.message(e);}});}
  saveVenue(){this.busy=true;this.modalError='';this.http.post('/api/venues',this.newVenue).subscribe({next:()=>{this.busy=false;this.change.markForCheck();this.close();this.load();this.notify('Venue created successfully.');},error:e=>{this.busy=false;this.change.markForCheck();this.modalError=this.message(e);}});}
  book(){
    if(!this.selectedSeats.length){this.modalError='Please select at least one seat.';return;}
    this.busy=true;this.modalError='';
    this.http.post<Booking>('/api/bookings',{eventId:this.selectedEvent?.id,customerName:this.customerName,email:this.email,seats:this.selectedSeats}).subscribe({next:b=>{this.busy=false;this.change.markForCheck();this.ticket=b;this.modal='ticket';this.load();this.notify('Booking confirmed. See you at the event!');},error:e=>{this.busy=false;this.change.markForCheck();this.modalError=this.message(e);if(e.status===409&&this.selectedEvent)this.http.get<SeatMap>(`/api/events/${this.selectedEvent.id}/seats`).subscribe(r=>{this.seatMap=r;this.selectedSeats=this.selectedSeats.filter(s=>!r.booked.includes(s));});}});
  }
  viewTicket(b:Booking){this.ticket=b;this.modalError='';this.modal='ticket';}
  requestCancel(b:Booking){this.ticket=b;this.modalError='';this.modal='cancel';}
  cancel(){if(!this.ticket)return;this.busy=true;this.http.post(`/api/bookings/${this.ticket.id}/cancel`,{}).subscribe({next:()=>{this.busy=false;this.change.markForCheck();this.close();this.load();this.notify('Booking cancelled. Seats are available again.');},error:e=>{this.busy=false;this.change.markForCheck();this.modalError=this.message(e);}});}
  checkIn(b:Booking){this.busy=true;this.http.post<Booking>(`/api/bookings/${b.id}/check-in`,{}).subscribe({next:r=>{this.busy=false;this.change.markForCheck();this.ticket=r;this.load();this.notify('Guest checked in successfully.');},error:e=>{this.busy=false;this.change.markForCheck();this.modalError=this.message(e);}});}
  downloadTicket(){if(!this.ticket)return;const b=this.ticket;this.download(`${b.reference}.txt`,`VENUEVISTA EVENTPRO\n\n${b.event.title}\n${new Date(b.event.startsAt).toLocaleString('en-IN')}\n${b.event.venue.name}, ${b.event.venue.city}\n\nBooking: ${b.reference}\nGuest: ${b.customerName}\nSeats: ${b.seats}\nAmount: ${this.money(b.total)}\nStatus: ${b.status}\n\nDemo ticket - payment is simulated.\n`,'text/plain');}
  exportSales(){const rows=[['Reference','Event','Guest','Seats','Amount INR','Status','Checked in','Booked at'],...this.bookings.map(b=>[b.reference,b.event.title,b.customerName,b.seats,b.total,b.status,b.checkedIn,b.bookedAt])];const safe=(v:unknown)=>{let s=String(v);if(/^[=+@\-\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};this.download('venuevista-sales.csv',rows.map(row=>row.map(safe).join(',')).join('\r\n'),'text/csv');this.notify('Sales report exported.');}
  download(name:string,body:string,type:string){const url=URL.createObjectURL(new Blob([body],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  venueEvents(id:number){return this.events.filter(e=>e.venue.id===id).length;}
  percentage(e:Event){return Math.round(e.sold/e.capacity*100);}
}
