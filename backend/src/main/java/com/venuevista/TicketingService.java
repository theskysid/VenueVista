package com.venuevista;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service @Transactional
public class TicketingService {
    private final EventRepository events;
    private final BookingRepository bookings;
    private final TicketRepository tickets;
    public TicketingService(EventRepository events, BookingRepository bookings, TicketRepository tickets) {
        this.events=events; this.bookings=bookings; this.tickets=tickets;
    }
    public Booking book(Requests.BookingInput input) {
        Event event=events.lockById(input.eventId()).orElseThrow(() -> missing("Event"));
        if (!event.startsAt.isAfter(LocalDateTime.now())) throw conflict("Ticket sales have closed for this event");
        List<String> seats=input.seats();
        if(seats==null || seats.isEmpty() || seats.size()>10 || new HashSet<>(seats).size()!=seats.size())
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Select 1 to 10 distinct seats");
        Set<String> taken=new HashSet<>();
        tickets.findByEventId(event.id).forEach(t -> taken.add(t.seat));
        for(String seat: seats) {
            if(seat==null || !seat.matches("[A-Z][1-9][0-9]?")) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Invalid seat label");
            int row=seat.charAt(0)-'A', col=Integer.parseInt(seat.substring(1));
            if(row>=event.venue.seatRows || col>event.venue.seatsPerRow) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Seat is outside this venue");
            if(taken.contains(seat)) throw conflict("Seat " + seat + " was already booked. Refresh and choose another seat.");
        }
        Booking booking=new Booking();
        booking.reference="VV-"+UUID.randomUUID().toString().substring(0,8).toUpperCase(Locale.ROOT);
        booking.event=event; booking.customerName=input.customerName().trim(); booking.email=input.email().trim();
        booking.seats=String.join(", ",seats); booking.total=event.price.multiply(BigDecimal.valueOf(seats.size()));
        booking.bookedAt=LocalDateTime.now(); bookings.saveAndFlush(booking);
        seats.forEach(seat -> tickets.save(new Ticket(event,booking,seat)));
        tickets.flush();
        return booking;
    }
    public Booking cancel(Long id) {
        Booking b=bookings.lockById(id).orElseThrow(() -> missing("Booking"));
        if(b.checkedIn) throw conflict("A checked-in booking cannot be cancelled");
        if(!b.status.equals("CANCELLED")) { b.status="CANCELLED"; tickets.deleteByBookingId(b.id); }
        return b;
    }
    public Booking checkIn(Long id) {
        Booking b=bookings.lockById(id).orElseThrow(() -> missing("Booking"));
        if(!b.status.equals("CONFIRMED")) throw conflict("A cancelled booking cannot be checked in");
        b.checkedIn=true; return b;
    }
    static ResponseStatusException missing(String label) {return new ResponseStatusException(HttpStatus.NOT_FOUND,label+" not found");}
    static ResponseStatusException conflict(String message) {return new ResponseStatusException(HttpStatus.CONFLICT,message);}
}
