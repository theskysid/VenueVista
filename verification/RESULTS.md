# VenueVista verification results

Verified on 24 November 2026 (Asia/Kolkata).

| Check | Observed result | Evidence |
| --- | --- | --- |
| Spring Boot compilation and executable package | PASS; runnable 1.0.0 JAR built | backend-build.log |
| Backend integration suite | PASS; 12 tests, 0 failures, 0 errors, 0 skipped | backend-tests.txt |
| Simultaneous same-seat booking | PASS; one success, one rejection, one active ticket | TicketingIntegrationTest concurrentBuyersCannotPurchaseSameSeat |
| Angular 21 production build | PASS | frontend-build.log |
| Docker Compose configuration | PASS | compose.yaml validated with docker compose config --quiet |
| Docker build and startup | PASS; Nginx, API and PostgreSQL running | docker-build-final.log and docker-status.txt |
| Full-stack PostgreSQL API workflow | PASS; creation, sale, conflict, analytics, cancellation, check-in, invalid input | docker-smoke-test.log |
| Persistent booking after API restart | PASS; reference, seats, amount, confirmed state and check-in retained | docker-persistence.log |
| Browser walkthrough | PASS; booking, check-in, search, export, venue/event creation, cancellation | screenshots 01 through 12 |
| Mobile viewport | Inspected at 390 by 844; navigation scrolls horizontally | screenshot 13 |
| Docker frontend in browser | PASS; final Angular build with PostgreSQL API data | screenshot 14 |
| Project report | Rendered and all 13 pages visually reviewed | submission report PDF and DOCX |
| Screenshot portfolio | 14 actual screens in a separate PDF and HTML gallery | submission screenshot PDF |

The default API port 8080 was occupied by an unrelated application. The verified Docker stack uses localhost ports 8091 (API) and 4301 (frontend); the configuration retains portable defaults 8080 and 4200 with environment overrides. Original temporary port-conflict logs are not included in the final evidence set.

Backend integration tests used isolated H2 storage. Docker workflow checks used PostgreSQL 17. Browser screenshots 01–13 used a separate local H2 session so their demonstration records differ from the Docker check dataset. Screenshot 14 shows the running Docker dataset. No real customer information or real payments were used. The first dataset contains 6 events and 3 venues; tests add their own records.

The tests validate the listed behavior at demonstration scale. Load testing, real payment testing, authentication testing, delivery integrations and QR scanning are outside the implemented scope.

## P_014 Java Batch 4 update

The primary container database is now Oracle Database Free. The earlier PostgreSQL checks above are historical evidence from the first project version; its data volume has been retained without automatic migration.

| Current check | Result | Evidence |
| --- | --- | --- |
| H2 backend integration suite | 12 tests passed, zero failures/errors/skips | ci-backend-h2.log |
| Oracle backend integration suite | 12 tests passed, zero failures/errors/skips in isolated test schema | ci-backend-oracle.log and oracle-tests.txt |
| Oracle-backed API ticket lifecycle | Passed through the Docker/Nginx frontend proxy | oracle-smoke-test.log |
| Oracle data persistence | Booking preserved after API restart | oracle-persistence.log |
| Angular production build | Passed | ci-frontend.log |
| Updated API Docker image | Built successfully with ojdbc11 | oracle-backend-image.log |
| GitHub Actions workflow syntax | Passed actionlint 1.7.7 | workflow-validation.log |
| Deployment success and failure paths | Five tests passed using a controlled Docker command substitute; includes rollback attempts | deployment-script-tests.log |
| Local and staging Compose syntax | Both validated with required dummy environment values | compose.yaml and deploy/compose.deploy.yaml |
| Deployment container health command | Verified inside the actual API runtime image | oracle-health.log plus local command verification |
| Report cover preservation | First 19 cover XML elements retained; before/after page images pixel-identical | report-cover-preservation.json |
| Report and screenshot deliverables | Updated report 16 pages, output document 15 actual screens | submission files |

The workflow is configured to test pull requests and main-branch changes, publish matching image tags to GHCR after passing checks, and deploy private staging when enabled. No Git remote or staging credentials are configured here, so hosted GitHub execution, registry publication and remote deployment are not claimed. Configure the repository and staging settings using docs/CI-CD.md to activate them.
