# BlueOffice Breach - Challenge: ReactoShell (Aramoon Student Space +
# internal staff tool), port 3001.
#
# Real vm2@3.9.19 (last version before the fix), genuinely vulnerable to
# the disclosed CVE-2023-37466 vm2 sandbox escape (Promise[@@species]
# handler sanitization bypass, CVSS 9.8) - not a hand-rolled simulation.

FROM node:20-alpine

LABEL challenge="blueoffice-reactoshell3001"

# bash is not part of alpine's base image; the intended reverse-shell
# path (`bash -i >& /dev/tcp/...`) needs it, since busybox's ash does
# not support /dev/tcp.
RUN apk add --no-cache bash

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev

COPY server.js ./
COPY lib ./lib
COPY site ./site
COPY public ./public

RUN mkdir -p /opt/aramoon \
    && printf 'CTF{Re4cT_T0_5hE11_EXp10t4T10n_5uCc2ss}\n' > /opt/aramoon/flag_reactoshell.txt \
    && printf '%s\n' \
        'Internal note - ReactoShell runs on vm2 for sandboxing untrusted' \
        'staff snippets. vm2 is pinned at 3.9.19 pending a dependency bump -' \
        'yes, we are aware that version range has a disclosed CVE' \
        '(CVE-2023-37466, Promise handler sanitization bypass). Tracked,' \
        'not yet scheduled. Access to this tool is staff-role gated, so' \
        'exposure is considered low.' \
        > /opt/aramoon/README_INTERNAL.txt \
    && printf '%s\n' \
        'TODO: rotate the staging DB creds before the next cohort demo day.' \
        'TODO: ask Nabil about the JWT secret rotation script.' \
        > /opt/aramoon/notes.txt \
    && addgroup -S reactoapp && adduser -S reactoapp -G reactoapp \
    && chown -R reactoapp:reactoapp /app /opt/aramoon \
    && chmod 400 /opt/aramoon/flag_reactoshell.txt

USER reactoapp

ENV PORT=3000
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/ >/dev/null || exit 1

CMD ["node", "server.js"]
