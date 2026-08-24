# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

BlueOffice Breach is an intentionally-vulnerable CTF lab: a single Oracle Cloud VM that runs one
Docker container per challenge, deployed via one `docker-compose.yml`. Each container simulates a
"machine" or service in a fictional company (BlueOffice) with a specific bug or misconfiguration
(command injection, SSTI, SQLi, LFI, SMB/FTP weak creds, SSH privesc, a real JBoss RCE + internal
SSRF pivot chain). Players enumerate the exposed ports, exploit each service, and recover flags.

This is the owner's own lab (not a shared/public writeup) — `FLAGS.md` and `SOLUTION.md` here are
the answer key and are never meant to reach players.

## Commands

```bash
scripts/build.sh        # docker compose build (creates .env from .env.example if missing)
scripts/start.sh         # docker compose up -d --build, then prints port map
scripts/stop.sh           # docker compose down
scripts/stop.sh --reset   # docker compose down --volumes --rmi local (full wipe/rebuild)
```

There is no test suite, linter, or package manager at the repo root — this is a collection of small,
independent service images, not a single application. Validate a change by rebuilding just that
service and curling/exercising its port(s), e.g.:

```bash
docker compose build <service-name> && docker compose up -d <service-name>
docker compose logs -f <service-name>
```

`PUBLIC_IP` in `.env` (copied from `.env.example`) is used only by the FTP challenge, for passive-mode
masquerade address; it's irrelevant to every other service.

## Architecture

- **One Docker service per challenge**, each in its own directory under `services/<name>/` with its
  own `Dockerfile` (Flask/Python apps also have `app.py` + `requirements.txt` + `templates/`). Ports
  are named after the challenge, e.g. `web80-command-injection`, `devpanel8000-sqli`, `lfi9999`.
- **Network isolation is the core security invariant**: every service gets its own dedicated bridge
  network in `docker-compose.yml` (`net_ftp`, `net_web80`, etc.) so a shell obtained in one challenge
  container has no network path to any other challenge or to the host. **`pivotnet` is the sole
  deliberate exception** — shared only by `rh-jboss` and `internal-api`, because that shared network
  *is* the challenge 9 pivoting puzzle (JBoss RCE on the public container, then pivot to reach an
  internal-only SSRF-vulnerable API that publishes no host port at all).
- **No host filesystem mounts, no `docker.sock`, no `privileged: true`, ever.** Every file a
  container needs is baked in at build time via Dockerfile `COPY`. When adding or editing a service,
  preserve this — don't introduce `volumes:` host binds or privileged mode.
- **`cap_drop: [ALL]` + `no-new-privileges` on every service where possible.** The two structural
  exceptions are `ssh2222-privesc` (sudo's setuid-root GTFOBins path requires the kernel to honor
  setuid, which `no-new-privileges` blocks) and `smb445`/`rh-jboss` daemons needing root to bind/switch
  UID. Don't add these flags to those services without understanding why they're absent — it will
  silently break the intended exploit path.
- **`mem_limit` / `pids_limit` on every service** so a compromised container (fork bombs, runaway
  processes) can't starve the host VM.
- Flags are baked into each container's filesystem (or delivered via localStorage/encoded tokens, per
  `FLAGS.md`) — never mounted from the host, never shared between containers.

## Working in this repo

- `README.md` is player-facing: port list and flavor text only, **no spoilers, no vulnerability
  hints**. `FLAGS.md` and `SOLUTION.md` are owner-only: exact flag values, locations, and full tested
  exploit steps. Keep this separation when editing — never leak solution detail into `README.md`.
- When adding a new challenge: give it its own `services/<name>/` directory and Dockerfile, its own
  bridge network in `docker-compose.yml` (unless it's deliberately part of a pivot chain like
  challenge 9), `cap_drop`/`no-new-privileges`/`mem_limit`/`pids_limit` unless the exploit path
  structurally requires otherwise, and matching entries in `README.md` (non-spoiler), `FLAGS.md`, and
  `SOLUTION.md` (full walkthrough with exact commands).
- Existing challenges are numbered/documented in the order they appear in `FLAGS.md` and
  `SOLUTION.md` — keep new entries numbered consecutively and cross-reference the same flag numbers
  across `README.md`/`FLAGS.md`/`SOLUTION.md`/`docker-compose.yml` comments.
