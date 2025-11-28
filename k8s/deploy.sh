#!/bin/bash
# Kubernetes Deployment Script for DigiBuddy

set -e

echo "🚀 Starting DigiBuddy Kubernetes Deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ docker is not installed. Please install it first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Step 1: Building Docker images...${NC}"

# Build backend image
echo "Building backend image..."
cd Backend_new
docker build -t digibuddy-backend:latest .
cd ..

# Build frontend image
echo "Building frontend image..."
docker build --build-arg VITE_API_BASE_URL=http://backend-service:8000/api -t digibuddy-frontend:latest .

# Check if using Minikube
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo -e "${YELLOW}📥 Loading images into Minikube...${NC}"
    minikube image load digibuddy-backend:latest
    minikube image load digibuddy-frontend:latest
fi

echo -e "${YELLOW}📋 Step 2: Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

echo -e "${YELLOW}🔐 Step 3: Checking secrets...${NC}"
if [ ! -f "k8s/secret.yaml" ]; then
    echo -e "${RED}❌ secret.yaml not found!${NC}"
    echo -e "${YELLOW}📝 Creating from example...${NC}"
    cp k8s/secret.example.yaml k8s/secret.yaml
    echo -e "${RED}⚠️  Please edit k8s/secret.yaml with your actual values before continuing!${NC}"
    echo -e "${YELLOW}Press Enter after editing secrets, or Ctrl+C to cancel...${NC}"
    read
fi
kubectl apply -f k8s/secret.yaml

echo -e "${YELLOW}⚙️  Step 4: Creating ConfigMap...${NC}"
kubectl apply -f k8s/configmap.yaml

echo -e "${YELLOW}🍃 Step 5: Deploying MongoDB...${NC}"
kubectl apply -f k8s/mongodb-deployment.yaml
echo "Waiting for MongoDB to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n digibuddy --timeout=300s || echo "MongoDB may still be starting..."

echo -e "${YELLOW}🔧 Step 6: Deploying Backend...${NC}"
kubectl apply -f k8s/backend-deployment.yaml

echo -e "${YELLOW}🎨 Step 7: Deploying Frontend...${NC}"
kubectl apply -f k8s/frontend-deployment.yaml

echo -e "${YELLOW}⏳ Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available deployment/backend -n digibuddy --timeout=300s || echo "Backend may still be starting..."
kubectl wait --for=condition=available deployment/frontend -n digibuddy --timeout=300s || echo "Frontend may still be starting..."

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${GREEN}📊 Current Status:${NC}"
kubectl get pods -n digibuddy
echo ""
echo -e "${GREEN}🌐 Access the application:${NC}"
echo "Frontend: http://localhost:30080"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View pods: kubectl get pods -n digibuddy"
echo "  View logs: kubectl logs -n digibuddy -l app=backend"
echo "  Port forward: kubectl port-forward -n digibuddy service/backend-service 8000:8000"

