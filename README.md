# IHRIS Reporting

## DOCKER INSTALLATION


# 📘 Installation Guide

## 1. Prerequisites
- Linux server (tested on **Ubuntu 22.04 LTS**)
- User with **sudo** access
- Git installed:
  ```bash
  sudo apt update && sudo apt install -y git
  ```
- Docker + Docker Compose installed:  
  Follow [this official guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04) or run:
  ```bash
  sudo apt install -y ca-certificates curl gnupg lsb-release
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  ```

> ✅ Check versions:  
> `docker --version`  
> `docker compose version`

---

## 2. Clone the Repository
```bash
git clone https://github.com/jeremielodi/ihris_reporting.git
cd ihris_reporting
```

---

## 3. Prepare Data Directory
Create a secure directory for database/data persistence:

```bash
mkdir ./data
chmod -R 700 ./data
```

---

## 4. Environment File
Copy the sample `.env` file:

```bash
cp .env_sample .env
```

Edit `.env` as needed for your environment (database credentials, ports, etc.).

---

## 5. Build & Run with Docker
Run the project with Docker Compose:

```bash
docker compose up --build --force-recreate --no-deps -d
```

This will:
- Build the Docker images
- Start containers in detached mode
- Recreate services to ensure fresh configs

---

## 6. Verify Installation
- Check running containers:
  ```bash
  docker ps
  ```
- Logs (if needed):
  ```bash
  docker compose logs -f
  ```
- Access the API:  
  Open [http://localhost:8282/docs](http://localhost:8282/docs) or replace `localhost` with your server’s IP/hostname.

---

## 7. (Optional) Manage Containers
- Stop:
  ```bash
  docker compose down
  ```
- Restart:
  ```bash
  docker compose restart
  ```

---

✅ At this point, **ihris-reporting-fastapi** should be up and running.




# 🔧 Manual Installation (No Docker)

## 0) Overview
- **Backend (FastAPI)** runs at `http://127.0.0.1:8282`
- **Frontend (Vue)** served by Nginx at `https://your-domain` (or `http://server-ip`)
- Reverse-proxy `/api` → FastAPI
- Logs & data live in `./data` and `./log` (or `/var/lib/ihris-reporting` & `/var/log/ihris-reporting` in prod)

---

## 1) System Prereqs (Ubuntu 22.04)
```bash
sudo apt update
sudo apt install -y build-essential curl git python3.11 python3.11-venv python3.11-dev                      postgresql postgresql-contrib nginx
```
> If `python3.11` isn’t available, use `python3.10` and replace commands accordingly.

---

## 2) Clone the Repo & Checkout Branch
```bash
git clone https://github.com/jeremielodi/ihris_reporting
cd ihris_reporting
```

---

## 3) Database (PostgreSQL)
Create DB, user, and grant:
```bash
sudo -u postgres psql
```
In the psql prompt:
```sql
CREATE USER ihris_reporting WITH PASSWORD 'strong-password';
CREATE DATABASE ihris_reporting_db OWNER ihris_reporting;
GRANT ALL PRIVILEGES ON DATABASE ihris_reporting_db TO ihris_reporting;
\q
```

Optional: allow local password auth (already default on Ubuntu). If you changed `pg_hba.conf`, reload:
```bash
sudo systemctl reload postgresql
```

---

## 4) Backend (FastAPI)

### 4.1 Create virtualenv & install deps
```bash
cd backend  # if your backend folder is named differently, adjust
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt  # or pip install fastapi uvicorn[standard] psycopg2-binary pydantic ...
```

### 4.2 Environment
Copy the sample and edit:
```bash
cp ../.env_sample ../.env   # or cp .env_sample .env if sample is in backend
```

**Minimal .env (example):**
```env
DB_HOST='127.0.0.1'
DB_NAME='ihris_manage'
DB_USER='ihris_user'
DB_PASSWORD='ihris_pwd'
DB_PORT='5432'

# sudo mkdir upload_dir_name && sudo chmod 777 it
# the upload dir is use both by docker or you local installation
UPLOAD_DIR='./data'
#docker params
POSTGRES_LOCAL_PORT=5434 # set the port for postgres external port
APP_LOCAL_PORT=8282  # set the backend port

#VITE_SERVER_URL='https://yourServer.com/'
VITE_SERVER_URL='http://localhost:8282/' # link use by the frontend to interact with the backend

WEB_CLIENT_PORT=8080 # frontend port
# for old ihris 'https://ihrisrdc.org/index.php/view'
VITE_RECORD_VIEW_URL='http://localhost:8080/#/manage/people_record_view'


# after 
METABASE_ENCRYPTION_KEY='config_your_secret_key_here'
METABASE_LOCAL_PORT=8383 # phisic machine metabase port
MB_QUERY_CACHING_ENABLED="true"
MB_QUERY_CACHING_MIN_TTL=300        # 5 minutes minimum
MB_QUERY_CACHING_MAX_TTL=3600      # 1 hour maximum
METABASE_API_URL='http://metabase:3000
/api'
METABASE_API_KEY=""


# Paths
DATA_DIR=./data
LOG_DIR=./log
```

> If your code reads config from `config/Database.py`, ensure it loads the above env vars or update the file accordingly.

### 4.3 Data & Logs
```bash
mkdir -p ./data ./log
chmod -R 700 ./data ./log
```

### 4.4 Migrations (if applicable)
If using Alembic:
```bash
alembic upgrade head
```
> Otherwise run your project’s provided SQL initializer scripts.

### 4.5 Run (development)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8282 --reload
```
> Replace `app.main:app` with your actual ASGI path.

### 4.6 Run (production) with systemd
Create unit:
```bash
sudo nano /etc/systemd/system/ihris-reporting.service
```
Paste:
```ini
[Unit]
Description=IHRIS Reporting FastAPI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ihris/ihris-reporting-fastapi/backend
Environment="PATH=/home/ihris/ihris-reporting-fastapi/backend/.venv/bin"
EnvironmentFile=/home/ihris/ihris-reporting-fastapi/.env
ExecStart=/home/ihris/ihris-reporting-fastapi/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8282 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ihris-reporting
sudo systemctl status ihris-reporting
```

---

## 5) Frontend (Vue.js)

### 5.1 Node.js (LTS) via nvm (recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts
```

### 5.2 Install deps & env
```bash
cd ../client  # adjust if your Vue project path differs
npm ci || npm install
cp .env.example .env.local  # or create .env.[mode]
```

**Minimal Vue env:**
```env
VITE_API_URL=/api   # use nginx reverse proxy
# or direct: VITE_API_URL=http://your-server:8282
```

### 5.3 Dev mode
```bash
npm run dev
# likely at http://localhost:5173
```

### 5.4 Build for production
```bash
npm run build
# This generates /dist
```

Install a simple static file server (optional for quick test):
```bash
npm i -g serve
serve -s dist -l 8080
```

---

## 6) Nginx (serve Vue & proxy API)
Copy built frontend to a web root:
```bash
sudo mkdir -p /var/www/ihris-reporting-ui
sudo rsync -a dist/ /var/www/ihris-reporting-ui/
sudo chown -R www-data:www-data /var/www/ihris-reporting-ui
```

Create an Nginx server block:
```bash
sudo nano /etc/nginx/sites-available/ihris-reporting.conf
```
Paste:
```nginx
server {
    listen 80;
    server_name your-domain your-server-ip;

    # Serve built Vue app
    root /var/www/ihris-reporting-ui;
    index index.html;

    # Frontend routes (history mode)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API reverse proxy to FastAPI
    location /api/ {
        proxy_pass         http://127.0.0.1:8282/;
        proxy_http_version 1.1;

        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        # websockets (if used)
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
    }

    # Static file caching (optional)
    location ~* \.(?:css|js|woff2?|ttf|eot|svg|png|jpe?g|gif)$ {
        expires 7d;
        add_header Cache-Control "public, no-transform";
        try_files $uri =404;
    }
}
```
Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/ihris-reporting.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6.1 SSL (Let’s Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain
```
Auto-renew runs via system timer.

---

## 7) CORS Notes
- In **backend**, allow the **frontend origin(s)** via environment (e.g., `CORS_ALLOW_ORIGINS=https://your-domain,http://localhost:5173`).
- If proxying `/api` with Nginx on the same domain, set `VITE_API_URL=/api` and CORS can be minimal.

---

## 8) Folders for caches & logs
You can keep them in the repo:
```bash
mkdir -p /home/ihris/ihris-reporting-fastapi/backend/{data,log}
chmod -R 700 /home/ihris/ihris-reporting-fastapi/backend/{data,log}
```
Or use system paths:
```bash
sudo mkdir -p /var/lib/ihris-reporting /var/log/ihris-reporting
sudo chown -R www-data:www-data /var/lib/ihris-reporting /var/log/ihris-reporting
```
Update your env (`DATA_DIR`, `LOG_DIR`) to match.

---

## 9) Verify
- API docs: `http://your-domain/api/docs` (via Nginx) or `http://server-ip:8282/docs` (direct)
- Frontend: `http://your-domain`

---

## 10) Useful service commands
```bash
# Backend
sudo systemctl status ihris-reporting
sudo journalctl -u ihris-reporting -f

# Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

## 11) Troubleshooting
- **502 Bad Gateway**: Backend not running or port mismatch. Check `ExecStart` path, `APP_PORT`, and `proxy_pass`.
- **CORS errors**: Make sure `CORS_ALLOW_ORIGINS` includes your frontend origin(s), or use same-domain `/api` proxy.
- **DB connection**: Confirm DB creds/host/port. From the server:
  ```bash
  PGPASSWORD=strong-password psql -h 127.0.0.1 -U ihris_reporting -d ihris_reporting_db -c '\dt'
  ```
- **Permissions**: Logs/data must be owned by the service user (e.g., `www-data`) and writable.
