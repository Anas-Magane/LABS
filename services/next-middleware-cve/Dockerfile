# BlueOffice Breach - Challenge: Next.js Middleware Auth Bypass (port 9000)
# Self-hosted production standalone Next.js build (not a static export).

FROM node:20-alpine

LABEL challenge="blueoffice-next-middleware-cve"

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build \
    && mkdir -p .next/standalone/.next \
    && cp -r .next/static .next/standalone/.next/static \
    && cp -r public .next/standalone/public

RUN addgroup -S nextapp && adduser -S nextapp -G nextapp \
    && chown -R nextapp:nextapp /app

USER nextapp

ENV PORT=3000
ENV HOSTNAME=0.0.0.0
ENV NODE_ENV=production

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/ >/dev/null || exit 1

CMD ["node", ".next/standalone/server.js"]
