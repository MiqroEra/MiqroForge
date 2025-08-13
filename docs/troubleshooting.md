### Common Installation Issues

#### 1. Insufficient Permissions Error
```bash
# Error message: Please run this script with sudo or root
# Solution: Run the script with sudo
sudo ./scripts/install_miqroforge.sh
```

#### 2. System Version Incompatibility
```bash
# Error message: This script only supports Ubuntu 20.04 or higher
# Solution: Ensure system version meets requirements
lsb_release -a
# Or upgrade to a supported version
```

#### 3. Docker Installation Failure
```bash
# Check Docker service status
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check Docker version
docker --version
docker-compose --version
```

#### 4. NFS Service Issues
```bash
# Check NFS service status
sudo systemctl status nfs-kernel-server

# Restart NFS service
sudo systemctl restart nfs-kernel-server

# Check NFS export configuration
cat /etc/exports
sudo exportfs -a

# Check NFS ports
sudo netstat -tulpn | grep :2049
```

#### 5. K3s Installation Failure
```bash
# Check K3s service status
sudo systemctl status k3s

# View K3s logs
sudo journalctl -u k3s -f

# Reinstall K3s
sudo k3s-uninstall.sh
# Then run the installation script again
```

#### 6. Container Startup Failure
```bash
# View container status
docker ps -a

# View container logs
docker logs miqroforge-web
docker logs miqroforge-mysql
docker logs miqroforge-minio

# Restart services
docker compose -f docker-compose.yaml restart

# Recreate and start services
docker compose -f docker-compose.yaml up -d --force-recreate
```

#### 7. Port Conflicts
```bash
# Check port usage
sudo netstat -tulpn | grep :30080
sudo netstat -tulpn | grep :3306
sudo netstat -tulpn | grep :9000

# Modify port configuration (edit docker-compose.yaml)
# Change 30080 to other available ports
```

#### 8. Insufficient Disk Space
```bash
# Check disk space
df -h

# Clean up Docker images and containers
docker system prune -a

# Clean up log files
sudo find /var/log -name "*.log" -delete
```

#### 9. Network Connection Issues
```bash
# Check network configuration
ip addr show

# Check firewall settings
sudo ufw status

# Allow necessary ports through firewall
sudo ufw allow 30080
sudo ufw allow 3306
sudo ufw allow 9000
sudo ufw allow 9001
```

#### 10. Python Dependency Issues
```bash
# Check Python version
python3 --version

# Reinstall dependencies
pip install -e . --break-system-packages --force-reinstall

# Clean pip cache
pip cache purge
```

### Viewing Logs

#### System Logs
```bash
# View system logs
sudo journalctl -f

# View specific service logs
sudo journalctl -u docker -f
sudo journalctl -u nfs-kernel-server -f
sudo journalctl -u k3s -f
```

#### Application Logs
```bash
# View MiqroForge logs
tail -f ./data/miqroforge/backend/logs/*.log

# View Docker container logs
docker logs -f miqroforge-web
```

### Reset Environment

If you encounter serious issues that require resetting the environment:

```bash
# Stop all services
docker compose -f docker-compose.yaml down

# Uninstall K3s
sudo k3s-uninstall.sh

# Clean up data directories
sudo rm -rf /data/miqroforge
sudo rm -rf ./data

# Run the installation script again
sudo ./scripts/install_miqroforge.sh
```

### Getting Help

If the above solutions cannot resolve your issue:

1. Check system logs for detailed error information
2. Confirm system meets minimum requirements
3. Search for similar issues in GitHub Issues
4. Submit a new Issue with detailed error information and system environment