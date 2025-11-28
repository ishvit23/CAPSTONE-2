# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the DigiBuddy application.

## Prerequisites

1. **Kubernetes cluster** (local or cloud)
   - Minikube: `minikube start`
   - Docker Desktop: Enable Kubernetes in settings
   - Cloud: GKE, EKS, AKS, etc.

2. **kubectl** installed and configured

3. **Docker** for building images

## Quick Start (Automated)

### Windows (PowerShell)
```powershell
.\k8s\deploy.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x k8s/deploy.sh
./k8s/deploy.sh
```

## Step-by-Step Deployment (Manual)

### Step 1: Build Docker Images

```bash
# Build backend image
cd Backend_new
docker build -t digibuddy-backend:latest .

# Build frontend image
cd ..
docker build -t digibuddy-frontend:latest .
```

### Step 2: Load Images into Kubernetes (for local clusters)

If using Minikube or Docker Desktop:
```bash
# For Minikube
minikube image load digibuddy-backend:latest
minikube image load digibuddy-frontend:latest

# For Docker Desktop (images are already available)
# No action needed
```

For cloud clusters, push to a container registry:
```bash
docker tag digibuddy-backend:latest your-registry/digibuddy-backend:latest
docker tag digibuddy-frontend:latest your-registry/digibuddy-frontend:latest
docker push your-registry/digibuddy-backend:latest
docker push your-registry/digibuddy-frontend:latest
```

Then update `image:` fields in deployment YAMLs.

### Step 3: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 4: Create Secrets

```bash
# Copy the example secret file
cp k8s/secret.example.yaml k8s/secret.yaml

# Edit secret.yaml with your actual values
# IMPORTANT: Never commit secret.yaml to git!

# Apply secrets
kubectl apply -f k8s/secret.yaml
```

### Step 5: Create ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

### Step 6: Deploy MongoDB

```bash
kubectl apply -f k8s/mongodb-deployment.yaml
```

Wait for MongoDB to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=mongodb -n digibuddy --timeout=300s
```

### Step 7: Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yaml
```

Check backend status:
```bash
kubectl get pods -n digibuddy -l app=backend
```

### Step 8: Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
```

### Step 9: (Optional) Deploy Ingress

If you have an ingress controller installed (nginx-ingress, traefik, etc.):

```bash
kubectl apply -f k8s/ingress.yaml
```

## Accessing the Application

### Using NodePort (Default)

Frontend: `http://localhost:30080` (or `http://<node-ip>:30080`)

Backend API: Access via frontend or port-forward:
```bash
kubectl port-forward -n digibuddy service/backend-service 8000:8000
# Then access at http://localhost:8000
```

### Using Ingress

If ingress is configured, access via the hostname specified in `ingress.yaml`:
- Frontend: `http://digibuddy.local`
- Backend: `http://digibuddy.local/api`

## Useful Commands

### Check Pod Status
```bash
kubectl get pods -n digibuddy
```

### View Logs
```bash
# Backend logs
kubectl logs -n digibuddy -l app=backend --tail=100

# Frontend logs
kubectl logs -n digibuddy -l app=frontend --tail=100

# MongoDB logs
kubectl logs -n digibuddy -l app=mongodb --tail=100
```

### Scale Deployments
```bash
kubectl scale deployment backend -n digibuddy --replicas=3
kubectl scale deployment frontend -n digibuddy --replicas=3
```

### Delete Everything
```bash
kubectl delete namespace digibuddy
```

## Troubleshooting

### Pods Not Starting
```bash
# Check pod events
kubectl describe pod <pod-name> -n digibuddy

# Check pod logs
kubectl logs <pod-name> -n digibuddy
```

### Image Pull Errors
- Ensure images are built and available
- For local clusters, use `minikube image load` or ensure Docker Desktop can access images
- For cloud, ensure images are pushed to registry and imagePullSecrets are configured

### Connection Issues
- Verify services are running: `kubectl get svc -n digibuddy`
- Check endpoints: `kubectl get endpoints -n digibuddy`
- Test connectivity: `kubectl exec -it <pod-name> -n digibuddy -- wget -O- http://backend-service:8000/api/chat/`

### MongoDB Connection Issues
- Verify MongoDB is running: `kubectl get pods -l app=mongodb -n digibuddy`
- Check MongoDB logs: `kubectl logs -l app=mongodb -n digibuddy`
- Verify MONGODB_URI in ConfigMap matches service name

## Production Considerations

1. **Use External MongoDB**: Consider using MongoDB Atlas or managed MongoDB service
2. **Use Secrets Management**: Use external secret management (Sealed Secrets, External Secrets Operator, etc.)
3. **Resource Limits**: Adjust resource requests/limits based on actual usage
4. **Persistent Storage**: Ensure MongoDB PVC is using appropriate storage class
5. **Monitoring**: Add Prometheus/Grafana for monitoring
6. **Logging**: Set up centralized logging (ELK, Loki, etc.)
7. **SSL/TLS**: Configure TLS certificates for ingress
8. **Backup**: Set up regular backups for MongoDB data

