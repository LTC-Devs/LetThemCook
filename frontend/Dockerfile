FROM node:22-alpine AS dependencies
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app

COPY --from=dependencies /app/node_modules /app/node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup -S -g 1001 unprivileged && \
	adduser -S -G unprivileged -u 1001 unprivileged

COPY --from=build /app/public /app/public
COPY --from=build --chown=unprivileged:unprivileged /app/.next/standalone /app
COPY --from=build --chown=unprivileged:unprivileged /app/.next/static /app/.next/static

USER unprivileged
EXPOSE 3000

CMD ["node", "server.js"]
