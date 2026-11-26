package com.venuevista;

import org.springframework.web.bind.annotation.*;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.http.HttpStatus;
import jakarta.validation.Valid;
import java.util.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@RestController @RequestMapping("/api") @Transactional(readOnly=true)
public class ApiController {
    private final VenueRepository venues;
    private final EventRepository events;
    private final BookingRepository bookings;
    private final TicketRepository tickets;
    private final TicketingService service;
    public ApiController(VenueRepository v, EventRepository e, BookingRepository b, TicketRepository t, TicketingService s) {
        venues=v;events=e;bookings=b;tickets=t;service=s;
    }
    @GetMapping("/venues") public List<Venue> venues(){return venues.findAll();}
    @PostMapping("/venues") @ResponseStatus(HttpStatus.CREATED) @Transactional
    public Venue createVenue(@Valid @RequestBody Requests.VenueInput r){return venues.save(new Venue(r.name().trim(),r.city().trim(),r.seatRows(),r.seatsPerRow()));}
    @GetMapping("/events") public List<Map<String,Object>> events(){
        return events.findAll().stream().sorted(Comparator.comparing(e->e.startsAt)).map(this::eventView).toList();
    }
    private Map<String,Object> eventView(Event e){
        return Map.of("id",e.id,"title",e.title,"category",e.category,"venue",e.venue,"startsAt",e.startsAt,"price",e.price,
                "color",e.color,"sold",tickets.countByEventId(e.id),"capacity",e.venue.seatRows*e.venue.seatsPerRow);
    }
    @PostMapping("/events") @ResponseStatus(HttpStatus.CREATED) @Transactional
    public Map<String,Object> createEvent(@Valid @RequestBody Requests.EventInput r){
        Venue v=venues.findById(r.venueId()).orElseThrow(()->TicketingService.missing("Venue"));
        return eventView(events.save(new Event(r.title().trim(),r.category(),v,r.startsAt(),r.price(),"violet")));
    }
    @GetMapping("/events/{id}/seats") public Map<String,Object> seats(@PathVariable Long id){
        Event e=events.findById(id).orElseThrow(()->TicketingService.missing("Event"));
        return Map.of("rows",e.venue.seatRows,"columns",e.venue.seatsPerRow,"booked",tickets.findByEventId(id).stream().map(t->t.seat).toList());
    }
    @GetMapping("/bookings") public List<Booking> bookings(){return bookings.findAll().stream().sorted(Comparator.comparing((Booking b)->b.bookedAt).reversed()).toList();}
    @PostMapping("/bookings") @ResponseStatus(HttpStatus.CREATED) @Transactional
    public Booking book(@Valid @RequestBody Requests.BookingInput r){return service.book(r);}
    @PostMapping("/bookings/{id}/cancel") @Transactional public Booking cancel(@PathVariable Long id){return service.cancel(id);}
    @PostMapping("/bookings/{id}/check-in") @Transactional public Booking checkIn(@PathVariable Long id){return service.checkIn(id);}
    @GetMapping("/analytics") public Map<String,Object> analytics(){
        List<Booking> active=bookings.findAll().stream().filter(b->b.status.equals("CONFIRMED")).toList();
        BigDecimal revenue=active.stream().map(b->b.total).reduce(BigDecimal.ZERO,BigDecimal::add);
        long count=tickets.count();
        int capacity=events.findAll().stream().mapToInt(e->e.venue.seatRows*e.venue.seatsPerRow).sum();
        List<Map<String,Object>> daily=new ArrayList<>();
        for(int i=6;i>=0;i--) {
            LocalDate date=LocalDate.now().minusDays(i);
            BigDecimal total=active.stream().filter(b->b.bookedAt.toLocalDate().equals(date)).map(b->b.total).reduce(BigDecimal.ZERO,BigDecimal::add);
            daily.add(Map.of("date",date,"revenue",total));
        }
        return Map.of("revenue",revenue,"ticketsSold",count,"events",events.count(),"venues",venues.count(),"capacity",capacity,
                "occupancy",capacity==0?0:Math.round(count*100.0/capacity),"daily",daily,"eventSales",events());
    }
}
