# BlueOffice Breach - Challenge 5: SMB (port 445)
#
# Like sshd, the Samba master daemon (smbd) must start as root to bind
# port 445 and switch UID per authenticated session - this is a
# structural requirement of Samba, not a relaxation of the isolation
# rules. The container still runs unprivileged, with no host mounts.

FROM ubuntu:22.04

LABEL challenge="blueoffice-smb445"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends samba samba-common-bin && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/log/samba /run/samba

# Share directories
RUN mkdir -p /srv/samba/public /srv/samba/hr /srv/samba/it /srv/samba/backups /srv/samba/secret

COPY shares/public/ /srv/samba/public/
COPY shares/hr/ /srv/samba/hr/
COPY shares/it/ /srv/samba/it/
COPY shares/backups/ /srv/samba/backups/
COPY shares/secret/ /srv/samba/secret/

COPY smb.conf /etc/samba/smb.conf

# SMB user with an intentionally weak, brute-forceable password
RUN useradd -M -s /usr/sbin/nologin Adam && \
    (echo "password123"; echo "password123") | smbpasswd -s -a Adam && \
    smbpasswd -e Adam

RUN chmod -R a+rX /srv/samba && \
    chown -R root:root /srv/samba

EXPOSE 445

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD bash -c 'echo > /dev/tcp/127.0.0.1/445' || exit 1

CMD ["/usr/sbin/smbd", "--foreground", "--no-process-group", "--debug-stdout"]
