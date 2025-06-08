# How to run

### Start minikube
minikube start

### Enable minikube container registry as principal while using the terminal (you'll need to re-run after opening a new terminal)
minikube addons enable registry minikube docker-env
minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Create a image
```bash
    docker build -t ws-server-blue-green ./ws-server
```

# Tag image to use on minukube registry
```bash
    docker tag ws-server-blue-green 127.0.0.1:5000/ws-server-blue-green
```

# Push to minukube registry
```bash
    docker push 127.0.0.1:5000/ws-server-blue-green
```

# Install Chart on Kubernetes
```bash
    helm install ws-server-blue-green-helm ./ws-server-blue-green-helm
```

# Port Forward
```bash
    minikube service ws-server-blue-green-helm
```

# Update to green version

```bash
    docker build -t ws-server-blue-green ./ws-server-blue-green
```

# Tag image to use on minukube registry
```bash
    docker tag ws-server-blue-green 127.0.0.1:5000/ws-server-blue-green
```

# Push to minukube registry
```bash
    docker push 127.0.0.1:5000/ws-server-blue-green
```

# Updating the chart
```bash
    helm upgrade ws-server-blue-green-helm ./ws-server-blue-green-helm
```

# Get pods
```bash
    kubectl get pods
```

# Scale replicas
```bash
    kubectl scale deployment ws-server-blue-green-helm --replicas=2
```

# Deleting the chart
```bash
    helm delete ws-server-blue-green-helm
```

# REDIS

## Start REDIS
helm install redis bitnami/redis --set auth.enabled=false