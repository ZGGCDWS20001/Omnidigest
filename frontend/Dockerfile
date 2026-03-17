# Frontend Dockerfile
# 前端 Dockerfile - 用于生产环境构建

# Stage 1: Build
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Install pnpm (optional, can also use npm)
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile || npm install

# Copy source code
COPY . .

# Build argument for API URL
# 使用 --build-arg VITE_API_URL=https://api.yourdomain.com 设置
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-}

# Build the application
RUN pnpm build || npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
