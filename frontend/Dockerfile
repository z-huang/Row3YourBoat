# --- Build Stage ---
FROM node:24-slim AS builder

WORKDIR /app

# 複製 package 管理相關檔案
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# 安裝 pnpm 並安裝依賴
RUN npm install -g pnpm && pnpm install

# 複製全部 frontend 原始碼
COPY frontend ./

# 建立 React 應用（產物會在 /app/build）
RUN pnpm run build

# --- Production Stage ---
FROM nginx:alpine

# 移除預設 nginx 網頁（可選）
RUN rm -rf /usr/share/nginx/html/*

# 複製建構好的 React 網頁到 nginx 預設網頁根目錄
COPY --from=builder /app/build /usr/share/nginx/html

# 可選：複製自訂 nginx 設定（如果你有）
# COPY nginx.conf /etc/nginx/nginx.conf

# 聲明開啟的 port
EXPOSE 80

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]


