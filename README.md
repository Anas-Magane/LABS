# BlueOffice Breach

## Story

BlueOffice is a small company that runs a single public machine on
Oracle Cloud. Over the years, an overworked sysadmin set up employee
file shares, a couple of internal dashboards, a dev panel, and a few
"temporary" services that were never properly decommissioned. Old
software was never patched, default and weak credentials were never
rotated, and at least one developer left credentials lying around in
places they shouldn't be.

Somewhere on this machine is a full chain of misconfigurations,
leaked credentials, and unpatched vulnerabilities. Your job: enumerate
everything, follow the breadcrumbs, and prove you can fully compromise
BlueOffice's infrastructure - all the way to root.

## Scope

This is a legal, intentionally-vulnerable CTF environment. The
following rules apply for the duration of the engagement:

- **In scope:** only the target IP address you were given, and only
  the ports listed below.
- **Do not** attack the underlying Oracle Cloud infrastructure, the
  hypervisor, or any other tenant/host on the network.
- **Do not** attempt to break out of, or escape, any Docker container.
  Every challenge is meant to be solved entirely inside its own
  container - if you find yourself trying to reach the host, you've
  gone off-script.
- **Do not** perform denial-of-service attacks (no flooding, no
  resource-exhaustion attacks, no destructive operations against
  shared services).
- **Do not** attack other players, if this is a shared/multi-player
  deployment.
- All shells you obtain are expected to be confined to a single
  challenge's container. That is by design, not a bug.
- The objective is simple: find and submit every flag.

## Target ports

| Port | Protocol | Service |
|------|----------|---------|
| 21   | TCP      | FTP |
| 80   | TCP      | Web application |
| 445  | TCP      | SMB |
| 2222 | TCP      | SSH |
| 3000 | TCP      | Web dashboard |
| 7777 | TCP      | HR recruitment portal |
| 8000 | TCP      | Dev Panel |
| 8888 | TCP      | Web application |
| 9999 | TCP      | Web application |
| 1000 | TCP      | Token-based web portal |
| 2000 | TCP      | System Time Viewer |
| 9000 | TCP      | Anas Education Platform |
| 9005 | TCP      | FST School Portal |
| 4000 | TCP      | BlueOffice Report Generator |
| 4500 | TCP      | BlueOffice ID Badge Photo Upload |
| 5432 | TCP      | Database service |

Have fun, enumerate thoroughly, and good luck.
