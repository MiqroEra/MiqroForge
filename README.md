> English | [中文](README_zh-CN.md) 

# MiqroForge Installation Script

This is an automated installation script for quickly deploying and configuring the MiqroForge microservice architecture platform on Linux systems. The script integrates a complete containerized runtime environment, including storage, database, web services, and other core components.

## Features

- **One-Click Deployment**: Automatically installs Docker, Python, NFS, K3s, and all other dependency components
- **Containerized Architecture**: Microservice deployment based on Docker Compose, supporting quick startup and scaling
- **Storage Integration**: Built-in MinIO object storage and MySQL database, providing complete data storage solutions
- **Kubernetes Ready**: Automatically installs K3s lightweight Kubernetes cluster, supporting container orchestration
- **Network Services**: Integrated NFS file sharing service, supporting distributed file systems
- **Web Interface**: Provides web-based management interface, accessible and manageable through browsers

## System Requirements

- Ubuntu >= 20.04 operating system
- Root privileges or sudo access
- Network connection (for downloading Docker, Python, NFS, K3s, and all other dependency components)
- Minimum 2GB RAM and 10GB disk space

## Usage

### Run after cloning the repository

```bash
# Clone the repository
git clone https://github.com/MiqroEra/MiqroForge.git
cd MiqroForge

# Run the installation script
sudo ./scripts/install_miqroforge.sh
```

## Installation Process

The script automatically executes the following steps:
- Install Docker and Docker Compose
- Install Python >= 3.8 and dependencies
- Install NFS Server
- Install K3s (lightweight Kubernetes distribution)
- Install MiqroForge v1.0 based on Docker Compose
    - [docker-compose.yaml](docker-compose.yaml)

## Kubernetes Installation

This script automatically installs K3s (lightweight Kubernetes distribution). If you need to use other Kubernetes distributions, please uninstall K3s first.
- Uninstall command:
```bash
sudo k3s-uninstall.sh
```

- Manually install Kubernetes, please refer to the following documents for reference:
    - [kubekey installation documentation](https://github.com/kubesphere/kubekey/blob/master/README.md)
    - [Kubernetes official documentation](https://kubernetes.io/docs/setup/)
- Modify miqroforge-web volume config in [docker-compose.yaml](docker-compose.yaml):
> Note: You need to replace `"<kubeconfig path>"` with the actual path to the kubeconfig file.
```yaml
... 
   web:
    ...
    volumes:
      ...
      - "<kubeconfig path>:/opt/project/miqroforge/backend/misc/k8s/config"
    ...
...
```
## Test

For details, please refer to: [test_cases.ipynb](tests/test_cases.ipynb)

## Troubleshooting
For details, please refer to: [troubleshooting.md](docs/troubleshooting.md)

## Documentation
For details, please refer to: [MiqroForge Documentation](https://miqroforge-docs.readthedocs.io/en/latest)