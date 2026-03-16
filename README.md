# KNBChat Server

FastAPI-based backend for a chat application.

## .env 配置（最小用例）

**1) 开发环境（本机 dev server）**

```env
APP_ENV=dev
```

**2) 生产环境（默认 Tauri Origin）**

```env
APP_ENV=prod
```

**3) 开发环境（真机调试，允许局域网地址）**

```env
APP_ENV=dev
TAURI_DEV_HOST="192.168.1.22"
```

**4) 生产环境（自定义允许的 Origin）**

```env
APP_ENV=prod
CORS_ALLOW_ORIGINS="tauri://localhost,http://tauri.localhost,https://your-web-domain.com"
```
