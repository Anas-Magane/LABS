# BlueOffice Breach - Challenge 9: BlueOffice HR Recruitment Portal (JBoss RCE)
# Player-facing port: 7777/tcp -> 8080 in container
#
# This is a REAL JBoss Application Server 4.0.5 (the well-known vulhub
# "JBoss JMXInvokerServlet / MainDeployer" lab image), not a simulation.
# The intended exploit path is the classic CVE-2010-0738-style
# unauthenticated jmx-console DeploymentFileRepository MBean abuse
# (exploit/multi/http/jboss_deploymentfilerepository), reached via
# /jmx-console and /jmx-console/HtmlAdaptor on port 7777. The base
# vulhub image ships jmx-console.war with BASIC auth (JBossAdmin role)
# enabled, so below we overwrite its web.xml/jboss-web.xml to strip
# that security-constraint/security-domain, exactly like the
# historical misconfigured JBoss 4.x/5.x deployments this module
# targets. The JMX invoker (jboss_invoke_deploy / jboss_maindeployer /
# jboss_bshdeployer) is left untouched and still works as a fallback.
FROM vulhub/jboss:as-4.0.5

LABEL challenge="blueoffice-rh-jboss"

# net-tools/python3 for post-exploitation enumeration inside the container.
# curl, wget, bash and iproute2 (ip) already ship with this base image.
RUN echo "deb http://archive.debian.org/debian jessie main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list && \
    apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -y --no-install-recommends --allow-unauthenticated net-tools python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Strip BASIC auth from the jmx-console HtmlAdaptor so
# exploit/multi/http/jboss_deploymentfilerepository can reach the
# jboss.admin:service=DeploymentFileRepository MBean without
# credentials.
COPY jmx-console-web.xml /opt/jboss/jboss4/server/default/deploy/jmx-console.war/WEB-INF/web.xml
COPY jmx-console-jboss-web.xml /opt/jboss/jboss4/server/default/deploy/jmx-console.war/WEB-INF/jboss-web.xml

# Themed BlueOffice HR Recruitment Portal, deployed as the JBoss ROOT
# webapp (auto-deployed exploded WAR) so it answers on / and every
# sub-page requested by the challenge (/hr, /careers, /candidates,
# /interviews, /upload-cv).
COPY webapp/ROOT /opt/jboss/jboss4/server/default/deploy/ROOT.war/

# Flag + note reachable after RCE, outside the JBoss deploy tree.
RUN mkdir -p /opt/hr-app
COPY flag7.txt /opt/hr-app/flag7.txt
COPY notes.txt /opt/hr-app/notes.txt
RUN chmod 444 /opt/hr-app/flag7.txt /opt/hr-app/notes.txt

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -sf http://127.0.0.1:8080/ -o /dev/null || exit 1

# Inherit the base image's CMD (run.sh -b 0.0.0.0) so JBoss listens on
# all interfaces inside the container.
