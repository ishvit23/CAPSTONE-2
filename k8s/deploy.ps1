# Kubernetes Deployment Script for DigiBuddy (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting DigiBuddy Kubernetes Deployment..." -ForegroundColor Cyan

# Check if kubectl is installed
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "❌ kubectl is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ docker is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

Write-Host "📦 Step 1: Building Docker images..." -ForegroundColor Yellow

# Build backend image
Write-Host "Building backend image..." -ForegroundColor Gray
Set-Location Backend_new
docker build -t digibuddy-backend:latest .
Set-Location ..

# Build frontend image
Write-Host "Building frontend image..." -ForegroundColor Gray
docker build --build-arg VITE_API_BASE_URL=http://backend-service:8000/api -t digibuddy-frontend:latest .

# Check if using Minikube
if (Get-Command minikube -ErrorAction SilentlyContinue) {
    $minikubeStatus = minikube status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "📥 Loading images into Minikube..." -ForegroundColor Yellow
        minikube image load digibuddy-backend:latest
        minikube image load digibuddy-frontend:latest
    }
}

Write-Host "📋 Step 2: Creating namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

Write-Host "🔐 Step 3: Checking secrets..." -ForegroundColor Yellow
if (-not (Test-Path "k8s/secret.yaml")) {
    Write-Host "❌ secret.yaml not found!" -ForegroundColor Red
    Write-Host "📝 Creating from example..." -ForegroundColor Yellow
    Copy-Item k8s/secret.example.yaml k8s/secret.yaml
    Write-Host "⚠️  Please edit k8s/secret.yaml with your actual values before continuing!" -ForegroundColor Red
    Write-Host "Press Enter after editing secrets, or Ctrl+C to cancel..." -ForegroundColor Yellow
    Read-Host
}
kubectl apply -f k8s/secret.yaml

Write-Host "⚙️  Step 4: Creating ConfigMap..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml

Write-Host "🍃 Step 5: Deploying MongoDB..." -ForegroundColor Yellow
kubectl apply -f k8s/mongodb-deployment.yaml
Write-Host "Waiting for MongoDB to be ready..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod -l app=mongodb -n digibuddy --timeout=300s 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "MongoDB may still be starting..." -ForegroundColor Yellow
}

Write-Host "🔧 Step 6: Deploying Backend..." -ForegroundColor Yellow
kubectl apply -f k8s/backend-deployment.yaml

Write-Host "🎨 Step 7: Deploying Frontend..." -ForegroundColor Yellow
kubectl apply -f k8s/frontend-deployment.yaml

Write-Host "⏳ Waiting for deployments to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available deployment/backend -n digibuddy --timeout=300s 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend may still be starting..." -ForegroundColor Yellow
}
kubectl wait --for=condition=available deployment/frontend -n digibuddy --timeout=300s 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend may still be starting..." -ForegroundColor Yellow
}

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Current Status:" -ForegroundColor Green
kubectl get pods -n digibuddy
Write-Host ""
Write-Host "🌐 Access the application:" -ForegroundColor Green
Write-Host "Frontend: http://localhost:30080"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View pods: kubectl get pods -n digibuddy"
Write-Host "  View logs: kubectl logs -n digibuddy -l app=backend"
Write-Host "  Port forward: kubectl port-forward -n digibuddy service/backend-service 8000:8000"

