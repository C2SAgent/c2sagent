# 阶段1：构建环境
FROM node:18-alpine AS builder
WORKDIR .
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 阶段2：运行环境
FROM nginx:alpine
COPY --from=builder /dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]