# VenueVista — EventPro Ticketing and Venue Management

A complete academic full-stack project using **Angular 21**, **Spring Boot 3.5.6**, **Java 21**, **Docker Compose**, and **Oracle Database Free**. Local development uses a persistent H2 database without requiring Oracle installation.

**Project P_014 · Java Batch 4 · Full Stack Development · Media and Entertainment**

The registered stack is Java, Spring Boot, Angular and Oracle DB. [Project registration](docs/PROJECT.md) and [CI/CD setup](docs/CI-CD.md) document the alignment.

## Quick start with Docker

Install Docker Engine or Docker Desktop with Compose, then run from this directory:

```bash
docker compose up --build -d
```

Open **http://localhost:4200**. The API is at http://localhost:8080/api and health is at http://localhost:4200/actuator/health. First startup downloads dependencies and images. Oracle initialization can take several minutes; inspect `docker compose logs -f db` until it is healthy. The container uses the maintained `gvenzl/oracle-free:23-slim` image, a dedicated `venuevista` application user and the `FREEPDB1` service. If the UI opens before the API is ready, click **Try again** after the backend starts.

```bash
docker compose logs -f backend      # inspect startup
docker compose ps                  # inspect container status
docker compose down                # stop; preserve Oracle data
```

The `venuevista-oracle` named volume persists bookings across container restarts. The Compose network keeps Oracle internal; frontend and API ports bind to localhost. `.env.example` documents the demo database password. Set both `ORACLE_PASSWORD` (database administrator) and `DB_PASSWORD` (application user) before using a shared environment.

If a default port is already occupied, use different host ports:

```bash
API_PORT=8091 UI_PORT=4301 docker compose up --build -d
# Open http://localhost:4301
```

For Windows PowerShell, set `$env:API_PORT="8091"` and `$env:UI_PORT="4301"` before running Compose, or put these values in a local `.env` file. This project was verified on ports 8091 and 4301. Use the same overrides when recreating the containers.

## Run without Docker

Prerequisites: JDK 21, Maven 3.9+, Node.js 20.19+ or 22.12+, npm. Internet is needed for the initial dependency installation.

One-command build and run on Linux/macOS:

```bash
bash scripts/run-local.sh
```

Open **http://localhost:4300**. Stop with Ctrl+C. This script builds the JAR, builds Angular, starts the API, and proxies `/api` through a small Node preview server. The API may need a few seconds after startup.

Alternatively, use two terminals (also suitable for Windows):

```bash
# Terminal 1
cd backend
mvn test package
java -jar target/venuevista-1.0.0.jar

# Terminal 2
cd frontend
npm ci
npm start
```

Open **http://localhost:4200**. Local data is stored in `backend/data/venuevista.mv.db`. H2 is a local convenience; Docker runs Oracle DB. The backend startup seeds data only when no venues exist: **3 venues, 6 upcoming events, 63 bookings, 126 tickets, INR 177,874 confirmed revenue**. Event dates are relative to first startup; sales charts cover the previous seven days. Only fictitious guest details are included.

## Features

- Dashboard: confirmed revenue, tickets sold, capacity occupancy, average admission value, seven-day revenue chart, and upcoming events.
- Events: create future events; search by event, venue or city; filter categories; show sales and capacity.
- Venues: create rectangular seating plans from 1–26 rows and 1–30 seats per row.
- Seating: select up to 10 seats; booked seats are disabled; live totals; validated guest name and email.
- Booking: transactional confirmation and a downloadable plain-text ticket.
- Guest list: search bookings; filter confirmed, checked-in and cancelled statuses; view tickets and check in guests.
- Cancellation: release seats, preserve history, and remove cancelled amounts from confirmed revenue. Checked-in bookings cannot be cancelled.
- Analytics: revenue and occupancy per event; CSV sales export including booking status.
- Database protection: pessimistic event lock and unique `(event_id, seat)` constraint prevent duplicate seat sales.
- Error handling: validation, missing records, invalid JSON, closed event and seat conflict messages.
- Responsive layouts, local fonts and keyboard focus styles.

## Demonstration walkthrough

1. Open Overview and inspect the seeded revenue and chart.
2. Open Events, search for `Midnight`, then open **View event & book seats**.
3. Select two available seats such as C5 and C6; enter a demonstration guest and `guest@example.com`.
4. Confirm the simulated booking. Inspect the reference, total and seats; download the ticket.
5. Open Bookings and search for the guest or reference. Open the ticket and click **Check in guest**.
6. Create a separate booking to demonstrate cancellation. Cancel it from Bookings; reopen its event and verify its seats are available.
7. Open Analytics and export the CSV. Compare confirmed revenue before and after booking or cancellation.
8. Add a venue in Venues, then create an event using it. Its seating plan appears automatically.

## Validation

```bash
cd backend
mvn test
cd ../frontend
npm ci
npm run build
cd ..
docker compose config --quiet
```

`backend/src/test/java/com/venuevista/TicketingIntegrationTest.java` contains 12 integration tests, including concurrent purchase contention, cancellation, check-in rules, price calculation, malformed inputs, seat boundaries, email validation, and analytics after cancellation. See `verification/` for actual build and verification evidence.

Exercise a running Docker application with the standard-library smoke script:

```bash
python3 scripts/smoke_test.py http://localhost:4200
```

This creates demonstration records. Set the URL to port 4301 if using the override above. The updated verification evidence distinguishes the earlier PostgreSQL demonstration from the Oracle database checks. The included logs show the Oracle API walkthrough and successful persistence after an API container restart. The screenshot portfolio contains 15 actual screens; the editable project report has 16 pages. The report body was updated with `scripts/update_report.py`, preserving the edited cover. The PDF report is an export of the DOCX using LibreOffice. Regenerate the screenshot PDF and HTML gallery with `python3 scripts/make_documents.py` after installing `Pillow` and `reportlab`. This script never modifies the report.

## CI/CD

GitHub Actions runs the backend suite on both H2 and an isolated Oracle schema, builds Angular, and builds both Docker images. Passing main-branch runs publish a matching image pair to GHCR. Configured staging deployments use SSH, readiness checks and automatic image rollback on failure. See [CI/CD instructions](docs/CI-CD.md) for repository variables, server preparation and secrets. The repository is hosted at https://github.com/theskysid/VenueVista. GitHub Actions runs on pull requests and pushes to main; remote staging requires the settings described in the CI/CD instructions.

## Source code repository

[VenueVista on GitHub](https://github.com/theskysid/VenueVista) contains the Spring Boot backend, Angular frontend, Docker configuration and GitHub Actions CI/CD workflow.

```bash
git clone https://github.com/theskysid/VenueVista.git
cd VenueVista
docker compose up --build -d
```

## Submission files

Reports and submission archives are separate academic deliverables; they are not included in this source repository.

- `submission/VenueVista-Project-Report.docx` — editable academic report.
- `submission/VenueVista-Project-Report.pdf` — print-ready report.
- `submission/VenueVista-Output-Screenshots.pdf` — captions and multiple actual application screenshots.
- `screenshots/` — original screenshots and `index.html` gallery.
- `submission/VenueVista-Submission.zip` — packaged project source, reports, screenshots, and verification evidence; excludes installed dependencies, live databases and build caches.
- `submission/VenueVista-Code.zip` — compact source-only package.

The report retains your saved cover. Project registration details in the body identify P_014, Java Batch 4, Full Stack Development, and Media and Entertainment. The student-edited front page is retained.

## Project structure

```text
backend/       Spring Boot entities, repositories, service, REST API and tests
frontend/      Angular standalone application, styles, models, Nginx and Dockerfile
scripts/       Local runner, build preview server and report generation source
docs/          Architecture diagrams and API documentation
screenshots/   Actual screen captures and HTML gallery
verification/  Build logs and verification results
submission/    Final reports and ZIP packages
compose.yaml   Frontend + backend + Oracle DB containers
```

## Scope and limitations

This is an organizer console for local academic evaluation. **It has no authentication or role authorization.** Do not expose it publicly or use real customer data. Payment, refunds and ticket verification are simulated; no email or SMS is sent, and no QR admission scanning is implemented. Event times use local wall-clock time, with Docker configured for Asia/Kolkata; multi-timezone event management is future work.

Venue and event creation are implemented; editing and deleting them are outside this version. All events are treated as published. The UI reloads data after operations but does not push seat updates between browsers; conflicts are checked at confirmation. Check-in is an administrative action and does not enforce event-day admission windows. The original booking record preserves cancelled seat labels and amounts, while active ticket rows are removed. Daily chart revenue is the current confirmed value grouped by booking date, so later cancellations adjust earlier days. CSV exports include all statuses for auditability. Event sales use a flat per-event ticket price. Reserved seating holds, payment idempotency, taxes, pricing tiers, migrations, pagination and audit logging are future extensions.

JPA `ddl-auto=update` is convenient for this submission. A production release should use reviewed schema migrations, access control, TLS, monitoring, rate limits and authenticated admission tokens.

## References

- [Angular version compatibility](https://angular.dev/reference/versions)
- [Spring Boot system requirements](https://docs.spring.io/spring-boot/3.5/system-requirements.html)
- [Spring Data JPA locking](https://docs.spring.io/spring-data/jpa/reference/jpa/locking.html)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Oracle Database Free container](https://github.com/gvenzl/oci-oracle-free)

Dependencies are pinned transitively in the npm lockfile and through the Spring Boot dependency BOM. Framework versions describe this implementation, not a claim that these are the newest releases.
