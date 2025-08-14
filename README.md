# [Readme中文](https://github.com/svipfun/VPigeonBot/releases/tag/Readme中文)
# VPigeonBot - Telegram Message Forwarding Bot

## Project Overview
`VPigeonBot` is a Python-based Telegram bot designed to forward user messages to a designated admin (`OWNER_ID`) and allow the admin to reply to users, block users, and more. It uses the `python-telegram-bot` library and runs in Webhook mode, ideal for deployment on a Linux server (e.g., Debian) with a public IP and standard ports (80, 443, 8443).

### Features
- Forwards user messages (text, photos, voice, videos, documents, stickers, etc.) to the admin.
- Admin can reply to messages, which are forwarded back to the original user.
- Supports `/start` and `/help` commands.
- Admin-only commands: `/block` (block a user), `/unblock` (unblock a user), `/listblocked` (view blocked users).
- Uses SQLite to store message mappings and blocked user lists.

---

## Deployment Steps
The following steps are tested on **Debian 11/12**, assuming the server has a public IP, supports standard ports (80, 443, 8443), and does not require port mapping.

### Prerequisites
- **Server**: Debian 11/12, 1 core, 1GB RAM, public IP, firewall allowing ports 80, 443, 8443.
- **Domain**: Resolved to the server’s public IP (e.g., `yourdomain.com`).
- **Telegram Bot**: Obtain `TOKEN` from [BotFather](https://t.me/BotFather) and admin `OWNER_ID` from [@userinfobot](https://t.me/userinfobot).
- **SSH Tool**: PuTTY or terminal for server access.

### Step 1: Prepare the Server Environment
1. **SSH into the Server**:
   ```
   ssh root@your-server-ip
   ```

2. **Update the System**:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Required Tools**:
   ```
   sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git -y
   ```

4. **Configure Firewall**:
   ```
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 8443/tcp
   sudo ufw reload
   ```

### Step 2: Obtain an SSL Certificate
Telegram Webhook requires HTTPS. Use Let's Encrypt to get a free certificate.
1. **Run Certbot**:
   ```
   sudo certbot --nginx -d yourdomain.com
   ```
   - Follow prompts: enter email, agree to terms, choose to redirect HTTP to HTTPS (select 2).
   - Certificates are generated at `/etc/letsencrypt/live/yourdomain.com/` (includes `fullchain.pem` and `privkey.pem`).

2. **Verify Certificates**:
   ```
   ls /etc/letsencrypt/live/yourdomain.com/
   ```

3. **Set Up Auto-Renewal**:
   - Certbot configures auto-renewal by default. Verify:
     ```
     sudo crontab -l
     ```

### Step 3: Configure Nginx
Nginx acts as a reverse proxy, forwarding HTTPS requests to the Bot’s local port (8443).
1. **Edit Configuration File**:
   ```
   sudo nano /etc/nginx/sites-available/default
   ```
   - Replace with the following (substitute `yourdomain.com` with your domain):
     ```
     server {
         listen 80;
         server_name yourdomain.com;
         return 301 https://$server_name$request_uri;
     }

     server {
         listen 443 ssl;
         server_name yourdomain.com;

         ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
         ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

         location /webhook {
             proxy_pass http://127.0.0.1:8443/webhook;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }
     ```

2. **Test Configuration**:
   ```
   sudo nginx -t
   ```

3. **Restart Nginx**:
   ```
   sudo systemctl restart nginx
   sudo systemctl status nginx
   ```

### Step 4: Deploy the Bot Code
1. **Create Project Directory**:
   ```
   mkdir /root/VPigeonBot
   cd /root/VPigeonBot
   ```

2. **Upload Code**:
   - Clone from GitHub (if uploaded):
     ```
     git clone https://github.com/your-username/VPigeonBot.git
     mv VPigeonBot/VPigeonBot.py .
     ```
   - Or upload locally:
     ```
     scp VPigeonBot.py root@your-server-ip:/root/VPigeonBot/
     ```

3. **Configure Code**:
   ```
   nano /root/VPigeonBot/VPigeonBot.py
   ```
   - Update the following:
     - `TOKEN = 'your-bot-token'` (from BotFather).
     - `OWNER_ID = your-telegram-id` (from @userinfobot).
     - Webhook settings:
       ```
       webhook_url="https://yourdomain.com/webhook"
       cert="/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
       key="/etc/letsencrypt/live/yourdomain.com/privkey.pem"
       ```
   - Save (Ctrl+O, Enter, Ctrl+X).

4. **Create Virtual Environment**:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install "python-telegram-bot[webhooks]"
   ```

5. **Test Run**:
   ```
   python3 /root/VPigeonBot/VPigeonBot.py
   ```
   - Verify logs show Webhook setup success (`HTTP/1.1 200 OK`).
   - Send `/start` or a message in Telegram to check if it forwards to `OWNER_ID`.

6. **Verify Webhook**:
   ```
   curl https://api.telegram.org/bot-your-token/getWebhookInfo
   ```
   - Confirm `"url": "https://yourdomain.com/webhook"`.

### Step 5: Run in Background
Use Systemd for persistent operation.
1. **Create Service File**:
   ```
   sudo nano /etc/systemd/system/vpigeonbot.service
   ```
   - Content:
     ```
     [Unit]
     Description=VPigeonBot
     After=network.target

     [Service]
     User=root
     WorkingDirectory=/root/VPigeonBot
     ExecStart=/root/VPigeonBot/venv/bin/python3 /root/VPigeonBot/VPigeonBot.py
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```

2. **Enable and Start**:
   ```
   sudo systemctl daemon-reload
   sudo systemctl start vpigeonbot
   sudo systemctl enable vpigeonbot
   sudo systemctl status vpigeonbot
   ```

---

## Common Issues and Troubleshooting
### 1. Nginx Configuration Errors
- **Error**: `sudo nginx -t` fails with `No such file or directory`.
  - **Cause**: Invalid link in `sites-enabled` (e.g., `vpigeonbot`).
  - **Solution**:
    ```
    ls -l /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/invalid-file
    sudo nginx -t
    sudo systemctl restart nginx
    ```
  - **My Error**: Encountered `open() "/etc/nginx/sites-enabled/vpigeonbot" failed` because the `vpigeonbot` file did not exist.
    - **Lesson**: Ensure `sites-enabled` only contains valid links (e.g., `default`). Always run `sudo nginx -t` after modifying configs.

### 2. Virtual Environment or File Missing
- **Error**: `source venv/bin/activate` reports `No such file or directory`.
  - **Cause**: Virtual environment not created or wrong path.
  - **Solution**:
    ```
    rm -rf /root/VPigeonBot/venv
    python3 -m venv /root/VPigeonBot/venv
    source /root/VPigeonBot/venv/bin/activate
    ```
  - **My Error**: `source /root/vpigeonbot/venv/bin/activate` failed because the directory was `/root/VPigeonBot` (case-sensitive).
    - **Lesson**: Linux is case-sensitive; always verify paths with `ls -l` or `find / -name VPigeonBot.py`.

- **Error**: `python3 VPigeonBot.py` reports `No such file or directory`.
  - **Solution**:
    ```
    ls /root/VPigeonBot/
    scp VPigeonBot.py root@your-server-ip:/root/VPigeonBot/
    ```

### 3. Dependency Issues
- **Error**: `RuntimeError: To use start_webhook, PTB must be installed via pip install "python-telegram-bot[webhooks]"`.
  - **Cause**: Missing Webhook dependencies.
  - **Solution**:
    ```
    source /root/VPigeonBot/venv/bin/activate
    pip install "python-telegram-bot[webhooks]"
    ```
  - **My Error**: Installed only `python-telegram-bot`, missing `[webhooks]` extension.
    - **Lesson**: Webhook mode requires `[webhooks]`; specify it during installation.

### 4. Webhook Setup Failure
- **Error**: `Bad webhook: webhook can be set up only on ports 80, 88, 443 or 8443`.
  - **Cause**: Webhook URL used a non-supported port (e.g., `50227`).
  - **Solution**: Use standard ports (`443` or `8443`) on a server with full port support.
    ```
    webhook_url="https://yourdomain.com/webhook"
    ```
  - **My Error**: Tried using port `50227`, not accepted by Telegram.
    - **Lesson**: Verify Telegram’s port requirements; prefer `443` for simplicity.

### 5. Other Issues
- **SSL Certificate Expiry**:
  ```
  sudo certbot renew
  ```
- **Port Conflicts**:
  ```
  sudo lsof -i :80
  sudo lsof -i :443
  sudo lsof -i :8443
  sudo kill <PID>
  ```
- **Log Checking**:
  - Nginx: `sudo cat /var/log/nginx/error.log`
  - Bot: `journalctl -u vpigeonbot -f`

---

## Notes
- **Security**: Do not expose `TOKEN` or `VPigeonBot.db`.
- **Backup**: Regularly back up the database (`/root/VPigeonBot/VPigeonBot.db`).
- **Case Sensitivity**: Linux is case-sensitive; always use `VPigeonBot.py` (uppercase).
- **Domain**: Ensure `yourdomain.com` resolves to the server’s public IP (`ping yourdomain.com`).
