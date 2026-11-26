package com.venuevista;

import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public final class Requests {
    private Requests() {}
    public record VenueInput(@NotBlank @Size(max=100) String name, @NotBlank @Size(max=100) String city,
                             @Min(1) @Max(26) int seatRows, @Min(1) @Max(30) int seatsPerRow) {}
    public record EventInput(@NotBlank @Size(max=120) String title,
                             @Pattern(regexp="Music|Conference|Theatre|Comedy|Workshop") @NotNull String category,
                             @NotNull Long venueId, @NotNull @Future LocalDateTime startsAt,
                             @NotNull @DecimalMin("1.00") @DecimalMax("100000.00") @Digits(integer=6,fraction=2) BigDecimal price) {}
    public record BookingInput(@NotNull Long eventId, @NotBlank @Size(max=100) String customerName,
                               @NotBlank @Email @Size(max=150) String email,
                               @NotEmpty @Size(max=10) List<@NotBlank String> seats) {}
}
