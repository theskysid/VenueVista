export interface Venue {id:number;name:string;city:string;seatRows:number;seatsPerRow:number}
export interface Event {id:number;title:string;category:string;venue:Venue;startsAt:string;price:number;color:string;sold:number;capacity:number}
export interface Booking {id:number;reference:string;event:Event;customerName:string;email:string;seats:string;total:number;bookedAt:string;status:string;checkedIn:boolean}
export interface Analytics {revenue:number;ticketsSold:number;events:number;venues:number;capacity:number;occupancy:number;daily:{date:string;revenue:number}[];eventSales:Event[]}
export interface SeatMap {rows:number;columns:number;booked:string[]}
