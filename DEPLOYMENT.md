# 部署指南 - Flask Academic Website

## 快速部署步骤

### 1. 准备工作

#### 1.1 本地准备
```bash
# 进入项目目录
cd /Users/quake0day/my_web/FlaskApp

# 初始化 Git 仓库（如果还没有）
git init
git add .
git commit -m "Initial commit with deployment configuration"

# 添加远程仓库
git remote add origin https://github.com/quake0day/Dodrio.git

# 推送代码
git push -u origin main
```

#### 1.2 GitHub 配置

在 GitHub 仓库设置中添加以下 Secrets（Settings → Secrets and variables → Actions）：

- **SERVER_HOST**: 你的 Debian 服务器 IP 地址或域名
- **SERVER_USER**: 服务器用户名（建议不要用 root）
- **SERVER_PORT**: SSH 端口（默认 22）
- **SERVER_SSH_KEY**: 你的 SSH 私钥内容

生成 SSH 密钥对（如果还没有）：
```bash
# 在本地生成密钥
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/deploy_key

# 查看私钥（用于 GitHub Secret）
cat ~/.ssh/deploy_key

# 查看公钥（添加到服务器）
cat ~/.ssh/deploy_key.pub
```

### 2. 服务器初始化

#### 2.1 连接到服务器
```bash
ssh your-user@your-server-ip
```

#### 2.2 添加 SSH 公钥
```bash
# 在服务器上
mkdir -p ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

#### 2.3 运行部署脚本
```bash
# 下载并运行部署脚本
wget https://raw.githubusercontent.com/quake0day/Dodrio/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 3. 配置域名和 SSL

#### 3.1 更新 Nginx 配置
```bash
sudo nano /etc/nginx/sites-available/flask-app
```

将 `server_name _;` 改为你的域名：
```nginx
server_name your-domain.com www.your-domain.com;
```

#### 3.2 安装 SSL 证书
```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 重启 Nginx
sudo systemctl reload nginx
```

### 4. 数据库迁移

如果你有现有的数据库需要迁移：

```bash
# 在本地导出数据库
cp db/information_.db db/information.db

# 将数据库文件添加到 Git（注意：只在初次部署时这样做）
git add -f db/information.db
git commit -m "Add initial database"
git push

# 或者通过 SCP 直接传输
scp db/information.db your-user@your-server:~/flask-app/db/
```

### 5. 自动部署配置

现在每次推送到 GitHub 的 main 分支，都会自动触发部署：

```bash
# 修改代码后
git add .
git commit -m "Update website"
git push

# GitHub Actions 会自动：
# 1. SSH 连接到服务器
# 2. 拉取最新代码
# 3. 重建 Docker 镜像
# 4. 重启容器
```

## 维护命令

### 查看日志
```bash
# 在服务器上
cd ~/flask-app
docker compose -f docker-compose.prod.yml logs -f
```

### 重启服务
```bash
docker compose -f docker-compose.prod.yml restart
```

### 更新手动部署
```bash
cd ~/flask-app
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### 备份数据库
```bash
# 创建备份
cp ~/flask-app/db/information.db ~/flask-app/db/backup_$(date +%Y%m%d).db

# 自动备份（添加到 crontab）
crontab -e
# 添加这行（每天凌晨 3 点备份）
0 3 * * * cp ~/flask-app/db/information.db ~/flask-app/db/backup_$(date +\%Y\%m\%d).db
```

## 故障排除

### 1. Docker 权限问题
```bash
# 添加用户到 docker 组
sudo usermod -aG docker $USER
# 重新登录或运行
newgrp docker
```

### 2. 端口被占用
```bash
# 查看端口占用
sudo lsof -i :5000
# 修改 docker-compose.prod.yml 中的端口
```

### 3. Nginx 配置错误
```bash
# 测试配置
sudo nginx -t
# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 4. GitHub Actions 失败
- 检查 Secrets 配置是否正确
- 查看 Actions 日志了解具体错误
- 确保服务器可以访问 GitHub

## 监控

### 设置健康检查
```bash
# 添加到 crontab
*/5 * * * * curl -f http://localhost:5000/health || docker compose -f ~/flask-app/docker-compose.prod.yml restart
```

### 查看资源使用
```bash
docker stats
```

## 安全建议

1. **使用防火墙**：只开放必要端口（22, 80, 443）
2. **定期更新**：`sudo apt-get update && sudo apt-get upgrade`
3. **备份数据**：定期备份数据库和重要文件
4. **监控日志**：定期检查应用和系统日志
5. **使用强密码**：为所有服务设置强密码
6. **限制 SSH**：考虑更改 SSH 端口，禁用密码登录

## 环境变量

在生产环境的 `.env` 文件中设置：

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database
DATABASE_PATH=/app/db/information.db

# Performance
GUNICORN_WORKERS=4
GUNICORN_THREADS=2

# Optional: Email settings for error reporting
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 联系支持

如有问题，请检查：
1. GitHub Actions 日志
2. Docker 容器日志：`docker compose -f docker-compose.prod.yml logs`
3. Nginx 错误日志：`/var/log/nginx/error.log`