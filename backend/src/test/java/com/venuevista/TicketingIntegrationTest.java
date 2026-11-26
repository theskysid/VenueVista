package com.venuevista;

import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.server.ResponseStatusException;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;
import static org.assertj.core.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties={
    "spring.datasource.url=${TEST_DB_URL:jdbc:h2:mem:tests;DB_CLOSE_DELAY=-1}",
    "spring.datasource.username=${TEST_DB_USER:sa}",
    "spring.datasource.password=${TEST_DB_PASSWORD:}",
    "spring.jpa.hibernate.ddl-auto=create-drop"})
@AutoConfigureMockMvc
class TicketingIntegrationTest {
    @Autowired TicketingService service;
    @Autowired VenueRepository venues;
    @Autowired EventRepository events;
    @Autowired TicketRepository tickets;
    @Autowired BookingRepository bookings;
    @Autowired MockMvc mvc;
    Event event;
    @BeforeEach void setUp(){Venue venue=venues.save(new Venue("Test venue","Test city",3,4));event=events.save(new Event("Test event","Music",venue,LocalDateTime.now().plusDays(30),new BigDecimal("499.50"),"violet"));}
    Requests.BookingInput input(String...seats){return new Requests.BookingInput(event.id,"Test Guest","test@example.com",List.of(seats));}
    @Test void bookingCalculatesAmountAndReservesSeats(){Booking b=service.book(input("A1","A2"));assertThat(b.total).isEqualByComparingTo("999.00");assertThat(tickets.countByEventId(event.id)).isEqualTo(2);}
    @Test void cancellationReleasesSeatsAndIsIdempotent(){Booking b=service.book(input("A1"));service.cancel(b.id);service.cancel(b.id);assertThat(tickets.countByEventId(event.id)).isZero();assertThat(service.book(input("A1")).status).isEqualTo("CONFIRMED");}
    @Test void duplicateSeatIsRejectedWithoutPartialSale(){service.book(input("A1"));assertThatThrownBy(()->service.book(input("A1","A2"))).isInstanceOf(ResponseStatusException.class);assertThat(tickets.countByEventId(event.id)).isEqualTo(1);}
    @Test void outOfRangeAndRepeatedSeatsAreRejected(){for(String s:List.of("Z1","A99","A0","AA1")){assertThatThrownBy(()->service.book(input(s))).isInstanceOf(ResponseStatusException.class);}assertThatThrownBy(()->service.book(input("A1","A1"))).isInstanceOf(ResponseStatusException.class);assertThat(tickets.countByEventId(event.id)).isZero();}
    @Test void checkedInBookingCannotBeCancelled(){Booking b=service.book(input("B1"));service.checkIn(b.id);assertThatThrownBy(()->service.cancel(b.id)).isInstanceOf(ResponseStatusException.class);assertThat(tickets.countByEventId(event.id)).isEqualTo(1);}
    @Test void cancelledBookingCannotBeCheckedIn(){Booking b=service.book(input("B1"));service.cancel(b.id);assertThatThrownBy(()->service.checkIn(b.id)).isInstanceOf(ResponseStatusException.class);}
    @Test void concurrentBuyersCannotPurchaseSameSeat() throws Exception {
        ExecutorService pool=Executors.newFixedThreadPool(2);CountDownLatch start=new CountDownLatch(1);
        try {Callable<Boolean> attempt=()->{start.await();try{service.book(input("C4"));return true;}catch(ResponseStatusException ex){return false;}};
            Future<Boolean> a=pool.submit(attempt), b=pool.submit(attempt);start.countDown();
            assertThat(List.of(a.get(15,TimeUnit.SECONDS),b.get(15,TimeUnit.SECONDS))).containsExactlyInAnyOrder(true,false);
            assertThat(tickets.countByEventId(event.id)).isEqualTo(1);
        }finally{pool.shutdownNow();}
    }
    @Test void requestValidationRejectsInvalidEmailAndNegativePrice() throws Exception {
        mvc.perform(post("/api/bookings").contentType("application/json").content("{\"eventId\":"+event.id+",\"customerName\":\"Guest\",\"email\":\"bad-email\",\"seats\":[\"A1\"]}")).andExpect(status().isBadRequest());
        mvc.perform(post("/api/events").contentType("application/json").content("{\"title\":\"Test\",\"category\":\"Music\",\"venueId\":"+event.venue.id+",\"startsAt\":\"2099-01-01T18:00:00\",\"price\":-1}")).andExpect(status().isBadRequest());
    }
    @Test void unknownEventReturns404() throws Exception {mvc.perform(get("/api/events/999999/seats")).andExpect(status().isNotFound());}
    @Test void analyticsExcludesCancelledRevenue() throws Exception {
        BigDecimal before=bookings.findAll().stream().filter(b->b.status.equals("CONFIRMED")).map(b->b.total).reduce(BigDecimal.ZERO,BigDecimal::add);
        Booking b=service.book(input("A3"));service.cancel(b.id);
        mvc.perform(get("/api/analytics")).andExpect(status().isOk()).andExpect(jsonPath("$.revenue").value(before.doubleValue()));
    }
    @Test void closedEventCannotSellTickets(){event.startsAt=LocalDateTime.now().minusDays(1);events.save(event);assertThatThrownBy(()->service.book(input("A1"))).isInstanceOf(ResponseStatusException.class);}
    @Test void malformedJsonAndOversizedVenueReturn400() throws Exception {
        mvc.perform(post("/api/venues").contentType("application/json").content("{\"name\":\"Hall\",\"city\":\"Pune\",\"seatRows\":27,\"seatsPerRow\":10}")).andExpect(status().isBadRequest());
        mvc.perform(post("/api/bookings").contentType("application/json").content("not json")).andExpect(status().isBadRequest());
    }
}
