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
git clone https://gitlab.com/Macara/ihris-reporting-fastapi
cd ihris-reporting-fastapi
```

---

## 3. Checkout the Integration Branch
```bash
git fetch origin ihris_manage_integration
git checkout ihris_manage_integration
```

---

## 4. Prepare Data Directory
Create a secure directory for database/data persistence:

```bash
mkdir ./data
chmod -R 700 ./data
```

---

## 5. Environment File
Copy the sample `.env` file:

```bash
cp .env_sample .env
```

Edit `.env` as needed for your environment (database credentials, ports, etc.).

---

## 6. Build & Run with Docker
Run the project with Docker Compose:

```bash
docker compose up --build --force-recreate --no-deps -d
```

This will:
- Build the Docker images
- Start containers in detached mode
- Recreate services to ensure fresh configs

---

## 7. Verify Installation
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

## 8. (Optional) Manage Containers
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




## Manual installation
## Configuration

### Database

Database connection parameters in config/Database.py

### Caches and logs

Create data and log directories

- mkdir data
- mkdir log
