# SECURITY.md

How BlueOffice Breach is isolated, and how to expose it safely on a
public Oracle Cloud VM.

## 1. Threat model

Every single challenge in this lab is an intentional remote code
execution / command injection / file read primitive. The assumption
is **hostile**: assume every container will be fully compromised by
every player. The entire design goal is that "fully compromised
container" still equals "zero impact on the Oracle Cloud host or any
other challenge."

## 2. Container isolation, challenge by challenge

| Challenge | Container | Runs as | Notable isolation |
|---|---|---|---|
| FTP (21) | `ftp-challenge` | non-root `ftpsvc` | `cap_drop: ALL`, no host mounts, backdoor bind-shell confined to container network namespace |
| Web cmdi (80) | `web80-command-injection` | non-root `webapp` | `cap_drop: ALL`, command injection chroot'd to container fs only |
| SSTI (3000) | `dashboard3000-ssti` | non-root `sstiuser` | `cap_drop: ALL`, Jinja2 RCE confined to container fs/process namespace |
| SSH + privesc (2222) | `ssh2222-privesc` | root (sshd) -> `chakir` -> root (via sudo misconfig) | No `cap_drop`/`no-new-privileges` (would break the intended sudo GTFOBins path), but no `--privileged`, no host mounts, no docker.sock |
| SMB (445) | `smb445` | root (smbd) -> `Adam` per session | `no-new-privileges:true`, no host mounts |
| Struts2 CVE (8888) | `struts8888` | non-root `struts` | `cap_drop: ALL`, simulated RCE confined to container fs |
| Dev Panel SQLi (8000) | `devpanel8000-sqli` | non-root `devpanel` | `cap_drop: ALL`, SQLite DB lives only inside the container |
| LFI (9999) | `lfi9999` | non-root `lfiuser` (whole Apache process, not just workers) | `cap_drop: ALL`, `include()` can only ever resolve paths that exist inside this container's filesystem |
| JBoss HR portal (7777) | `rh-jboss` | root (JBoss 4's own startup scripts require it) | `cap_drop: ALL`, `no-new-privileges:true`, real-but-legacy RCE confined to this container; the only host on its network besides itself is `internal-api` (by design - see below) |
| Internal HR API (not published) | `internal-api` | non-root `hrapi` | `cap_drop: ALL`, no ports published to the host at all - reachable only from `rh-jboss` over the dedicated `pivotnet` network |

## 3. Rules enforced across every service

- **No `network_mode: host`.** Every container is on its own
  dedicated bridge network (`net_ftp`, `net_web80`, `net_dashboard3000`,
  `net_ssh2222`, `net_smb445`, `net_struts8888`, `net_devpanel8000`,
  `net_lfi9999`). Containers cannot reach one another - a shell
  obtained in one challenge has no network path into any other
  challenge's container, let alone the host. The one deliberate
  exception is `pivotnet`, shared only by `rh-jboss` and
  `internal-api` - that shared network *is* challenge 9's pivoting
  puzzle, and it does not touch any other challenge's network.
- **No host filesystem mounts.** Every file each container needs
  (flags, web content, configs) is baked into the image at build time
  via `COPY` in the Dockerfile. There isn't a single `volumes:` host
  bind-mount anywhere in `docker-compose.yml`. There is nothing on the
  host filesystem for an exploit to reach even if it tried.
- **No `/var/run/docker.sock` mounted anywhere.** No container can
  talk to the Docker daemon, so no container can spawn sibling
  containers, inspect other containers, or escape via the classic
  docker.sock-mount technique.
- **No `privileged: true` anywhere.** Every container runs with the
  default (non-privileged) Docker security profile: standard seccomp
  filter, standard AppArmor/SELinux profile, no access to host
  devices, no ability to load kernel modules, no `CAP_SYS_ADMIN`.
- **`cap_drop: [ALL]`** on every service where it doesn't break
  required behaviour (all six non-root services). SSH and SMB keep
  the Docker default capability set because their master daemons
  structurally require root (binding, per-session UID switching) -
  exactly like they would on a bare-metal server - but they are still
  fully sandboxed by the container boundary itself.
- **`pids_limit` and `mem_limit`** on every service, so a fork bomb or
  runaway process inside an exploited container cannot starve the
  Oracle Cloud VM of CPU, memory, or PIDs.
- **Reverse shells and bind shells never leave the container.** Every
  RCE primitive in this lab (FTP backdoor, SSTI, Struts2) spawns a
  process that is a child of that container's own PID namespace. A
  reverse shell connecting *out* to a player's listener is just a
  normal outbound network connection from the container (the same as
  any legitimate outbound traffic) - it does not, and cannot, grant
  access to the host's filesystem, processes, or other containers.

## 4. Why SSH and SMB are different

`sshd` and `smbd` are two of the only services on earth that
*structurally* require root to start: they bind a socket, then drop
privileges per-connection by switching UID to the authenticated user.
This is normal, expected behavior on a real server, and is exactly
what makes the SSH challenge's "log in as a normal user, then privesc
to root" flow meaningful in the first place — that's the
intentionally designed "main machine" experience this challenge is
meant to represent.

Root inside the `ssh2222-privesc` container is **not** root on the
Oracle Cloud VM. The container has no extra capabilities, no
`--privileged` flag, no shared PID/network/mount namespace with the
host, and no mounted host paths. Becoming root inside that one
container is the literal goal of the challenge — it is contained by
the same Docker boundary as every other service here.

## 5. Hardening the Oracle Cloud host itself

The containers are isolated from the host by design, but you should
still harden the VM that runs them:

1. **Security List / Network Security Group (Oracle Cloud console):**
   only open inbound ingress rules for the 9 challenge ports:
   `21, 80, 445, 2222, 3000, 7777, 8000, 8888, 9999/tcp`, plus `6200/tcp`
   and `21100-21110/tcp` (required for the FTP challenge's backdoor
   and passive-mode data channel — see `docker-compose.yml`). Do
   **not** open `5000/tcp` or `internal-api`'s dashboard port
   anywhere — that service has no `ports:` entry in
   `docker-compose.yml` at all and must stay reachable only from
   `rh-jboss` over the internal `pivotnet` network. Do not
   open the VM's real SSH management port (22) to the world; use a
   different port or restrict it to your own IP via a separate
   security rule.
2. **Host firewall (`ufw`/`firewalld`/`iptables`):** mirror the same
   allow-list locally, default-deny everything else inbound.
3. **Do not run `docker compose` as a user with passwordless sudo to
   root for anything other than Docker itself.** Treat the host the
   same way you'd treat any internet-facing box.
4. **Keep Docker Engine itself patched.** The isolation guarantees
   above rely on the container runtime's namespace/cgroup/seccomp
   enforcement being intact and up to date.
5. **Monitor resource usage** (`docker stats`) periodically - the
   `mem_limit`/`pids_limit` settings will keep a single exploited
   container from taking down the host, but you should still watch
   for abuse.
6. **Reset between engagements.** Use `scripts/stop.sh --reset` to
   tear down all containers/images and rebuild clean for the next
   group of players - this guarantees no state (uploaded webshells,
   modified files, leftover backdoor connections) carries over.
7. **Never expose the Docker daemon's TCP socket** (`-H tcp://...`)
   on this host. Compose talks to the local Unix socket only.

## 6. What "isolated" does *not* mean here

Containers can still make **outbound** connections to the public
internet (e.g. so a reverse shell from the SSTI or Struts2 challenge
can connect back to a player's listener — this is intended, expected
CTF behavior and mirrors how a real pentest engagement works). What
they cannot do is reach the Oracle Cloud host's filesystem/processes,
the Docker daemon, or any other challenge's container. If you want to
further restrict outbound traffic (e.g. to prevent containers being
used to scan the wider internet), add egress firewall rules at the
Oracle Cloud Security List / host iptables level — Docker Compose
networking alone does not restrict egress by default.
