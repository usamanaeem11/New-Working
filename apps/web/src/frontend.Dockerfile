# Multi-stage build for Next.js
FROM node:20-alpine as base
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Dependencies
FROM base as deps
COPY package.json package-lock.json ./
RUN npm ci --only=production && \
    npm cache clean --force

# Builder
FROM base as builder
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production
FROM base as production
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]
