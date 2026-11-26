package com.venuevista;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
public class Booking {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @Column(unique = true, nullable = false) public String reference;
    @ManyToOne(optional = false) public Event event;
    public String customerName;
    public String email;
    public String seats;
    @Column(precision = 12, scale = 2) public BigDecimal total;
    public LocalDateTime bookedAt;
    public String status = "CONFIRMED";
    public boolean checkedIn;
}
