# BlueOffice Breach - Challenge: File Upload Extension Bypass RCE (port 4500)
# PHP + Apache, running fully as a non-root user on an unprivileged
# internal port, same pattern as the LFI challenge.

FROM php:8.2-apache

LABEL challenge="blueoffice-file-upload-bypass"

# Listen on an unprivileged port so the whole stack can run as non-root
RUN sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY apache-vhost.conf /etc/apache2/sites-available/000-default.conf

# Dedicated low-privileged user for the entire Apache process
# (master + workers) - no setuid/setgid step is needed at runtime.
RUN useradd -r -u 10002 -d /var/www -s /usr/sbin/nologin uploaduser

COPY html/ /var/www/html/
COPY flag_upload.txt /var/www/flag_upload.txt

RUN mkdir -p /var/www/html/uploads /var/log/apache2 /var/run/apache2 /var/lock/apache2 && \
    chown -R uploaduser:uploaduser /var/www /var/log/apache2 /var/run/apache2 /var/lock/apache2 && \
    chmod 770 /var/www/html/uploads && \
    chmod 640 /var/www/flag_upload.txt

ENV APACHE_RUN_USER=uploaduser
ENV APACHE_RUN_GROUP=uploaduser
ENV APACHE_PID_FILE=/var/run/apache2/apache2.pid
ENV APACHE_RUN_DIR=/var/run/apache2
ENV APACHE_LOCK_DIR=/var/lock/apache2
ENV APACHE_LOG_DIR=/var/log/apache2

USER uploaduser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fs http://127.0.0.1:8080/ || exit 1

CMD ["apache2-foreground"]
