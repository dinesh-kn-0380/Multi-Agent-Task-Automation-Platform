# ── Stage 1: Python Backend Builder ──────────────────────────────────────────
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# ── Stage 2: Node.js Frontend Builder ────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy chatbot-ui-base (cloned repo)
COPY chatbot-ui-base/package.json chatbot-ui-base/package-lock.json ./
RUN npm ci --prefer-offline

COPY chatbot-ui-base/ .

# Copy our custom frontend extensions
COPY frontend/components/ ./components/multi-agent-ext/
COPY frontend/styles/ ./app/styles/
COPY frontend/types/ ./types/

# Build the Next.js app
RUN npm run build

# ── Stage 3: Final Production Image ──────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Install Node.js for the Next.js server
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app/backend /app/backend

# Copy built Next.js app
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder /app/frontend/node_modules /app/frontend/node_modules
COPY --from=frontend-builder /app/frontend/package.json /app/frontend/package.json
COPY --from=frontend-builder /app/frontend/public /app/frontend/public

# Copy startup script
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Environment defaults (override at runtime)
ENV PORT_BACKEND=5000
ENV PORT_FRONTEND=3000
ENV FLASK_DEBUG=false
ENV NEXT_PUBLIC_BACKEND_URL=http://localhost:5000

EXPOSE 3000 5000

CMD ["/app/start.sh"]
