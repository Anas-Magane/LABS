# BlueOffice Breach - Challenge 8: LFI (port 9999)
# PHP + Apache, running fully as a non-root user on an unprivileged
# internal port. include() vulnerability can only ever read files that
# exist inside THIS container's filesystem - there are no host mounts.

FROM php:8.2-apache

LABEL challenge="blueoffice-lfi9999"

# Listen on an unprivileged port so the whole stack can run as non-root
RUN sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf

RUN a2enmod rewrite

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY apache-vhost.conf /etc/apache2/sites-available/000-default.conf

# Dedicated low-privileged user for the entire Apache process
# (master + workers) - no setuid/setgid step is needed at runtime.
RUN useradd -r -u 10001 -d /var/www -s /usr/sbin/nologin lfiuser

COPY html/ /var/www/html/
COPY flag6.txt /var/www/flag6.txt

RUN mkdir -p /var/log/apache2 /var/run/apache2 /var/lock/apache2 && \
    chown -R lfiuser:lfiuser /var/www /var/log/apache2 /var/run/apache2 /var/lock/apache2 && \
    chmod 640 /var/www/flag6.txt && chown lfiuser:lfiuser /var/www/flag6.txt

ENV APACHE_RUN_USER=lfiuser
ENV APACHE_RUN_GROUP=lfiuser
ENV APACHE_PID_FILE=/var/run/apache2/apache2.pid
ENV APACHE_RUN_DIR=/var/run/apache2
ENV APACHE_LOCK_DIR=/var/lock/apache2
ENV APACHE_LOG_DIR=/var/log/apache2

USER lfiuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fs http://127.0.0.1:8080/robots.txt || exit 1

CMD ["apache2-foreground"]
