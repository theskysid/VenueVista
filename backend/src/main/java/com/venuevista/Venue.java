package com.venuevista;

import jakarta.persistence.*;

@Entity
public class Venue {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) public Long id;
    @Column(nullable = false) public String name;
    @Column(nullable = false) public String city;
    public int seatRows;
    public int seatsPerRow;
    protected Venue() {}
    public Venue(String name, String city, int rows, int columns) {
        this.name = name; this.city = city; this.seatRows = rows; this.seatsPerRow = columns;
    }
}
