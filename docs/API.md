# VenueVista REST API

Base path: `/api`. JSON requests and responses. This local demonstration does not use authentication. Monetary values are INR; the backend uses Java BigDecimal. Dates use ISO local date/time strings without a timezone offset.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/venues` | All venues |
| POST | `/venues` | Create venue; 201 |
| GET | `/events` | Events with capacity and active tickets sold |
| POST | `/events` | Create future event; 201 |
| GET | `/events/{id}/seats` | Rows, columns, booked seat labels |
| GET | `/bookings` | Booking history, newest first |
| POST | `/bookings` | Confirm up to 10 distinct seats; 201 |
| POST | `/bookings/{id}/cancel` | Cancel and release active tickets |
| POST | `/bookings/{id}/check-in` | Mark confirmed booking checked in |
| GET | `/analytics` | Confirmed revenue, occupancy, daily totals and event sales |

```json
// POST /venues
{"name":"Riverside Hall","city":"Bengaluru","seatRows":6,"seatsPerRow":10}

// POST /events (use a future date and an existing venueId)
{"title":"Campus Live","category":"Music","venueId":1,"startsAt":"2099-12-10T18:00:00","price":799.00}

// POST /bookings
{"eventId":1,"customerName":"Demo Guest","email":"guest@example.com","seats":["C5","C6"]}

// GET /events/1/seats (example)
{"rows":8,"columns":12,"booked":["A1","A2"]}

// Error response (example)
{"message":"Seat C5 was already booked. Refresh and choose another seat."}
```

Examples are illustrative; actual IDs and availability depend on the stored data. Categories: Music, Conference, Theatre, Comedy, Workshop. Price: 1.00–100000.00, maximum two decimal places. Venue dimensions: 1–26 rows and 1–30 columns. Customer name: 1–100 characters; email: valid address, maximum 150 characters. Seats follow A1–Z30 within the venue's dimensions. Empty, repeated or unavailable seats are rejected. The server computes the total and reference; clients cannot set them.

HTTP statuses: 200 for reads and lifecycle changes; 201 for creation; 400 for validation or malformed input; 404 for unknown record IDs; 409 for unavailable seats, closed sales or invalid lifecycle changes.

Cancellation is idempotent for an already cancelled booking. Check-in is idempotent for an already checked-in confirmed booking. A checked-in booking cannot be cancelled. A cancelled booking cannot be checked in. Creating a booking is **not idempotent**: avoid automatically retrying after an uncertain network outcome; inspect the guest list first.

Health endpoint outside the API prefix: `GET /actuator/health`.
