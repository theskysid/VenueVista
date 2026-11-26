# VenueVista P_014 CI/CD

**Batch:** Java Batch 4. **Track:** Full Stack Development. **Industry:** Media and Entertainment.

The workflow is `.github/workflows/ci-cd.yml`. The source repository is https://github.com/theskysid/VenueVista. Pushes to main and pull requests trigger CI. Staging deployment remains optional and requires the configuration below.

## Continuous integration

Pull requests, pushes to `main`, and manual workflow dispatch run these checks:

1. Java 21 compilation and all backend integration tests with isolated H2 storage.
2. The same integration tests against an Oracle Database Free service and a disposable `venuevista_test` schema.
3. `npm ci` using the committed lockfile and the Angular production build on Node.js 22.
4. Compose validation, shell syntax checks, deployment success/failure-path tests, and both Docker image builds, after the test jobs pass.

The workflow uploads backend/Oracle test results and the compiled Angular application as artifacts. Official GitHub Actions are pinned to verified commit SHAs, with their major versions noted in comments. Test database passwords are disposable CI values, not staging credentials. The Oracle job runs `ddl-auto=create-drop`; never point these test variables at a real application schema.

## Continuous delivery

Successful `main` runs publish this pair to GitHub Container Registry:

```text
ghcr.io/<owner>/<repository>/backend:sha-<full-commit-sha>
ghcr.io/<owner>/<repository>/frontend:sha-<full-commit-sha>
```

Both use the same release tag. Pull request jobs build images without publishing or accessing deployment secrets. Publication uses the workflow's scoped `GITHUB_TOKEN`; no Docker Hub account is needed. Release metadata and the deployment scripts are uploaded as a deployment artifact.

## Configure private staging once

The application remains a private organizer demonstration because it has no login. The staging Compose file exposes only the UI on the server's loopback address. Access it through an SSH tunnel. Do not use this deployment as a public ticket store.

1. Create a Linux staging server with Docker Engine, Compose v2 with `up --wait`, Bash, curl, Python 3 and `flock`. Allow enough memory for Oracle and Java; a server with at least 4 GB RAM is a practical starting point for this demo, not a measured capacity claim.
2. Create `/opt/venuevista`, owned by the deployment user. Copy `deploy/.env.example` to `/opt/venuevista/.env`; enter private database passwords and set `UI_PORT`. Restrict the file to the deployment user (`chmod 600 .env`). Oracle passwords apply when its data volume is initialized; changing this file does not rotate an existing database password.
3. If the GHCR packages are private, log in to GHCR **on that server** using a read-only package token. Give the server account access to both image packages. No registry token is transferred by the workflow.
4. Create a GitHub environment called `staging`, restricted to `main`. Add the secrets below and optionally configure an environment reviewer where your GitHub plan supports one.
5. Set repository variable `ENABLE_STAGING_DEPLOY` to `true`. The deployment job is skipped until this explicit configuration is made. Push to `main` or run the workflow manually on `main`.

| Setting | Type | Value or purpose |
| --- | --- | --- |
| `ENABLE_STAGING_DEPLOY` | Repository variable | `true` enables automatic staging deployment after passing CI |
| `SSH_HOST` | Staging secret | Server DNS name or IPv4 address, without a URL scheme |
| `SSH_USER` | Staging secret | Linux user that owns the deployment directory and can use Docker |
| `SSH_PRIVATE_KEY` | Staging secret | Deployment key for that user |
| `SSH_KNOWN_HOSTS` | Staging secret | Verified server host key entry, including `[host]:port` for a nonstandard port |
| `SSH_PORT` | Variable | Optional; defaults to `22` |
| `DEPLOY_DIR` | Variable | Optional; defaults to `/opt/venuevista`; use a path without spaces |

Keep the database passwords in the server `.env`, not in GitHub source or workflow logs. Configure the GitHub repository to require the backend, Oracle, frontend and image-build checks before merging.

## Deployment and rollback behavior

The deployment job checks the SSH host key, copies the deployment Compose file and helpers, and invokes `deploy.sh` with the verified image identity. The script takes an exclusive lock, validates configuration, pulls the image pair and starts the stack. Compose waits for Oracle, the API and the frontend health checks. A final read-only check verifies health through Nginx, the Angular page, and the event API.

Successful releases are stored in `releases/sha-<commit>.env`; `current.env` records the active version and `previous.env` records the preceding one. If startup or readiness fails, the script attempts to restore the previous image pair and reports failure. It does not delete the Oracle volume, claim zero downtime, or undo schema changes. `ddl-auto=update` is suitable for the current academic demo; incompatible schema changes require a backup and migration plan before a release.

Manual rollback on the staging server:

```bash
cd /opt/venuevista
# Substitute the full SHA tag of a previously published successful release.
bash deploy.sh owner/repository sha-0123456789abcdef0123456789abcdef01234567
```

View the private application through a tunnel:

```bash
ssh -L 4301:127.0.0.1:4200 user@staging-host
# Open http://localhost:4301 on your computer.
```

## Reproduce the checks locally

```bash
mvn -B -ntp -f backend/pom.xml verify
npm --prefix frontend ci
npm --prefix frontend run build
docker compose config --quiet
bash -n scripts/deploy.sh scripts/check_health.sh scripts/run-local.sh
python3 scripts/test_deploy.py
# Start the Oracle stack and wait for the first database initialization.
docker compose up --build -d
bash scripts/check_health.sh http://localhost:4200
python3 scripts/smoke_test.py http://localhost:4200
```

The smoke script creates sample records. Automated deployment uses the read-only health helper instead, so deployments do not create fake sales. To run the integration suite against an external **disposable Oracle test schema**, set `TEST_DB_URL`, `TEST_DB_USER`, and `TEST_DB_PASSWORD` before `mvn verify`.

## References

- [GitHub container publication](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- [GitHub deployment environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [Oracle Free container maintainer documentation](https://github.com/gvenzl/oci-oracle-free)
