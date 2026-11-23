FROM node:22-alpine AS build
RUN apk add --no-cache libc6-compat
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/root/.npm \
	npm ci --prefer-offline --no-audit --no-fund

COPY . .
RUN --mount=type=cache,target=/app/.next/cache \
	npm run build

FROM alpine:3.21 AS runner
WORKDIR /app

ENV NODE_ENV=production \
	NEXT_TELEMETRY_DISABLED=1 \
	PORT=3000 \
	HOSTNAME=0.0.0.0

RUN apk add --no-cache nodejs \
	&& addgroup -S -g 1001 unprivileged \
	&& adduser -S -G unprivileged -u 1001 unprivileged

COPY --from=build --chown=unprivileged:unprivileged /app/public /app/public
COPY --from=build --chown=unprivileged:unprivileged /app/.next/standalone /app
COPY --from=build --chown=unprivileged:unprivileged /app/.next/static /app/.next/static

USER unprivileged
EXPOSE 3000

CMD ["node", "server.js"]
