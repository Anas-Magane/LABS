# BlueOffice Breach - Challenge 4: SSH + Privilege Escalation (port 2222)
#
# This is the one challenge where "root inside the container" is part
# of the intended design (the GTFOBins-style sudo misconfiguration is
# the whole point). sshd itself must run as root to do privilege
# separation - this is normal and required for any SSH server. The
# container itself still runs WITHOUT --privileged, without host
# bind-mounts, and without docker.sock, so root-in-container never
# equals root-on-the-Oracle-Cloud-host.

FROM ubuntu:22.04

LABEL challenge="blueoffice-ssh2222-privesc"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server sudo findutils && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/sshd

# Low-privileged player account
RUN useradd -m -s /bin/bash chakir && \
    echo 'chakir:H4RD_P4SS_BR0_20262026' | chpasswd

COPY flag4.txt /home/chakir/flag4.txt
COPY note.txt /home/chakir/note.txt
RUN chown chakir:chakir /home/chakir/flag4.txt /home/chakir/note.txt && \
    chmod 440 /home/chakir/flag4.txt && \
    chmod 444 /home/chakir/note.txt

# Root flag, only reachable through the intended privilege escalation
COPY flag5.txt /root/flag5.txt
RUN chown root:root /root/flag5.txt && chmod 600 /root/flag5.txt

# Intentional GTFOBins-style misconfiguration: chakir can run `find`
# as root with no password -> `sudo find . -exec /bin/sh \; -quit`
RUN echo 'chakir ALL=(ALL) NOPASSWD: /usr/bin/find' > /etc/sudoers.d/chakir && \
    chmod 440 /etc/sudoers.d/chakir && \
    visudo -c

COPY sshd_config /etc/ssh/sshd_config
RUN chmod 600 /etc/ssh/sshd_config && ssh-keygen -A

EXPOSE 22

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD bash -c 'echo > /dev/tcp/127.0.0.1/22' || exit 1

CMD ["/usr/sbin/sshd", "-D", "-e"]
