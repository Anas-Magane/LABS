# BlueOffice Breach - Challenge 16: PostgreSQL Weak Credentials (port 5432)
#
# Official, multi-arch PostgreSQL image (works natively on the Oracle Cloud
# ARM64 host, no emulation needed). The only thing baked in at build time is
# the seed SQL - no host bind-mounts, per repo convention. Credentials and
# the default database name are supplied via environment variables in
# docker-compose.yml (POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB),
# intentionally left as the weak postgres/postgres pair for this challenge.
#
# The official image already listens on all interfaces and allows remote
# password authentication for any host by default (host all all all
# scram-sha-256 in the generated pg_hba.conf) - exactly what this challenge
# needs, so no extra pg_hba.conf/postgresql.conf overrides are required.

FROM postgres:16

LABEL challenge="blueoffice-postgres5432-weak-creds"

COPY postgres-init/ /docker-entrypoint-initdb.d/

EXPOSE 5432

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
    CMD pg_isready -U postgres -d blueoffice || exit 1
