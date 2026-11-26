package com.venuevista;
import org.springframework.data.jpa.repository.*;
import jakarta.persistence.LockModeType;
import java.util.Optional;
public interface BookingRepository extends JpaRepository<Booking, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE) @Query("select b from Booking b where b.id = :id")
    Optional<Booking> lockById(Long id);
}
