package com.venuevista;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface TicketRepository extends JpaRepository<Ticket, Long> {
    List<Ticket> findByEventId(Long eventId);
    void deleteByBookingId(Long bookingId);
    long countByEventId(Long eventId);
}
