FROM node:24-slim AS builder
WORKDIR /app

COPY slacking-app/package.json slacking-app/package-lock.json ./
RUN npm install

COPY slacking-app ./
RUN npm run build

FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/build /etc/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]