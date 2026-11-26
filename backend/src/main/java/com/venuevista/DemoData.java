package com.venuevista;

import org.springframework.stereotype.Component;
import org.springframework.boot.CommandLineRunner;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.*;
import java.util.*;

@Component
public class DemoData implements CommandLineRunner {
    private final VenueRepository venues; private final EventRepository events; private final BookingRepository bookings; private final TicketRepository tickets;
    public DemoData(VenueRepository v,EventRepository e,BookingRepository b,TicketRepository t){venues=v;events=e;bookings=b;tickets=t;}
    @Override @Transactional public void run(String...args){
        if(venues.count()>0) return;
        Venue amph=venues.save(new Venue("The Grand Amphitheatre","Bengaluru",8,12));
        Venue hall=venues.save(new Venue("Skyline Convention Center","Mumbai",6,10));
        Venue studio=venues.save(new Venue("Studio 24","Pune",5,8));
        String[] titles={"Midnight in Bloom","The Future of Everything","A Night at the Theatre","Unfiltered Live","The Sunday Sessions","Design Beyond Screens"};
        String[] cats={"Music","Conference","Theatre","Comedy","Music","Workshop"};
        String[] colors={"violet","blue","rose","orange","teal","blue"};
        Venue[] vs={amph,hall,amph,studio,studio,hall};
        int[] prices={1499,2499,899,699,1199,1799};
        String[] people={"Aarav Sharma","Priya Mehta","Ishaan Patel","Ananya Rao","Rohan Kapoor","Meera Iyer","Kabir Singh","Diya Nair"};
        for(int i=0;i<6;i++){
            Event e=events.save(new Event(titles[i],cats[i],vs[i],LocalDate.now().plusDays(5+i*3).atTime(18+i%3,0),BigDecimal.valueOf(prices[i]),colors[i]));
            for(int j=0;j<8+i;j++){
                Booking b=new Booking(); b.reference=String.format("VV-DEMO%02d%02d",i+1,j+1);b.event=e;b.customerName=people[j%8];
                b.email="guest"+(i*20+j)+"@example.com";int n=j*2;
                b.seats=seat(n,e.venue.seatsPerRow)+", "+seat(n+1,e.venue.seatsPerRow);
                b.total=e.price.multiply(BigDecimal.valueOf(2));b.bookedAt=LocalDate.now().minusDays((j+i)%7).atTime(10+j%8,15);
                b.checkedIn=false; bookings.save(b);
                tickets.save(new Ticket(e,b,seat(n,e.venue.seatsPerRow)));tickets.save(new Ticket(e,b,seat(n+1,e.venue.seatsPerRow)));
            }
        }
    }
    private String seat(int n,int cols){return ""+(char)('A'+n/cols)+(n%cols+1);}
}
