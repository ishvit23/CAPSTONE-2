# Kubernetes Setup Guide

## Problem: Authentication Required Error

If you're seeing "Authentication required" errors, you need to either:
1. Set up a local Kubernetes cluster, OR
2. Configure authentication for your cloud cluster

## Option 1: Local Kubernetes Cluster (Recommended for Development)

### Using Docker Desktop (Easiest)

1. **Enable Kubernetes in Docker Desktop:**
   - Open Docker Desktop
   - Go to Settings → Kubernetes
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"
   - Wait for Kubernetes to start (green indicator)

2. **Verify it's working:**
   ```powershell
   kubectl cluster-info
   kubectl get nodes
   ```

### Using Minikube

1. **Install Minikube:**
   ```powershell
   # Using Chocolatey
   choco install minikube
   
   # Or download from: https://minikube.sigs.k8s.io/docs/start/
   ```

2. **Start Minikube:**
   ```powershell
   minikube start
   ```

3. **Verify:**
   ```powershell
   kubectl get nodes
   ```

### Using Kind (Kubernetes in Docker)

1. **Install Kind:**
   ```powershell
   choco install kind
   ```

2. **Create a cluster:**
   ```powershell
   kind create cluster --name digibuddy
   ```

3. **Verify:**
   ```powershell
   kubectl get nodes
   ```

## Option 2: Cloud Cluster Authentication

If you're using a cloud cluster (GKE, EKS, AKS), you need to authenticate:

### Google Cloud (GKE)
```powershell
gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE --project PROJECT_ID
```

### AWS (EKS)
```powershell
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION
```

### Azure (AKS)
```powershell
az aks get-credentials --resource-group RESOURCE_GROUP --name CLUSTER_NAME
```

## Quick Fix: Skip Validation (Not Recommended)

If you just want to test without fixing authentication, you can skip validation:

```powershell
kubectl apply -f k8s/namespace.yaml --validate=false
```

**⚠️ Warning:** This skips important validation checks. Only use for testing.

## Verify Your Setup

After setting up a cluster, verify everything works:

```powershell
# Check cluster connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check current context
kubectl config current-context
```

## Next Steps

Once you have a working cluster:

1. **Set up secrets:**
   ```powershell
   Copy-Item k8s\secret.example.yaml k8s\secret.yaml
   # Edit secret.yaml with your values
   ```

2. **Deploy:**
   ```powershell
   .\k8s\deploy.ps1
   ```

## Troubleshooting

### "No context set" error
- Make sure Kubernetes is enabled in Docker Desktop, OR
- Start Minikube with `minikube start`, OR
- Configure your cloud cluster credentials

### "Authentication required" error
- Your kubectl is pointing to a cluster that needs authentication
- Set up a local cluster (Docker Desktop is easiest)
- Or authenticate with your cloud provider

### "Connection refused" error
- Kubernetes cluster is not running
- Check Docker Desktop Kubernetes status
- Or restart Minikube: `minikube start`

