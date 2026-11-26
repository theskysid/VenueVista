package com.venuevista;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity @Table(name = "events")
public class Event {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @Column(nullable = false) public String title;
    public String category;
    @ManyToOne(optional = false) public Venue venue;
    public LocalDateTime startsAt;
    @Column(precision = 12, scale = 2) public BigDecimal price;
    public String color;
    protected Event() {}
    public Event(String title, String category, Venue venue, LocalDateTime startsAt, BigDecimal price, String color) {
        this.title = title; this.category = category; this.venue = venue; this.startsAt = startsAt; this.price = price; this.color = color;
    }
}
