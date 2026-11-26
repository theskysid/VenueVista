package com.venuevista;

import jakarta.persistence.*;

@Entity @Table(uniqueConstraints = @UniqueConstraint(columnNames = {"event_id", "seat"}))
public class Ticket {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @ManyToOne(optional = false) public Event event;
    @ManyToOne(optional = false) public Booking booking;
    @Column(nullable = false) public String seat;
    protected Ticket() {}
    public Ticket(Event event, Booking booking, String seat) { this.event = event; this.booking = booking; this.seat = seat; }
}
