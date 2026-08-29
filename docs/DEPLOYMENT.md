# Deployment Guide: `hi-bel`

This guide covers deploying `hi-bel` to **Railway**, **Render**, and **VPS / Docker**.

---

## 1. Deploying to Railway

1. Push your repository to GitHub.
2. In the [Railway Dashboard](https://railway.app/), click **New Project > Deploy from GitHub repo**.
3. Select `agos-services`.
4. Add a **PostgreSQL** database and a **Redis** instance from the Railway template gallery.
5. In the service settings, configure the following environment variables:
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<Generate a random 64-char key>`
   - `ALLOWED_HOSTS`: `*`
   - `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
   - `REDIS_URL`: `${{Redis.REDIS_URL}}`
   - `SHOPIFY_API_KEY`: `<Shopify Admin Access Token>`
   - `SHOPIFY_API_SECRET`: `<Shopify App API Secret>`
   - `SHOPIFY_STORE_DOMAIN`: `<your-store.myshopify.com>`
   - `MCP_AUTH_REQUIRED`: `True`
6. Set the start command:
   ```bash
   python manage.py migrate && uvicorn config.asgi:application --host 0.0.0.0 --port $PORT --workers 4
   ```

---

## 2. Deploying to Render

1. Create a new **Web Service** on [Render](https://render.com/).
2. Select your GitHub repository.
3. Configure:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `uvicorn config.asgi:application --host 0.0.0.0 --port $PORT --workers 4`
4. Add a **Render PostgreSQL** and set `DATABASE_URL`.
5. Add environment variables for Shopify API credentials.

---

## 3. Deploying to VPS with Docker & Nginx

### Docker Compose
Run the stack using Docker Compose:
```bash
docker compose up -d --build
```

### Nginx Reverse Proxy Configuration (`/etc/nginx/sites-available/hi-bel`)
```nginx
server {
    listen 80;
    server_name mcp.yourdomain.com;

    location /mcp/sse {
        proxy_pass http://127.0.0.1:8000/mcp/sse;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Disable buffering for SSE streams
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
