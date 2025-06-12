# How to run

### Start minikube
```bash
minikube start
```

### Enable minikube container registry as principal while using the terminal (you'll need to re-run after opening a new terminal)
```bash
minikube addons enable registry minikube docker-env
minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

### Start REDIS
```bash
    helm install redis bitnami/redis --set auth.enabled=false
```

### Create a image
```bash
    docker build -t ws-server-blue-green:0.0.1 ./ws-server
```

### Tag image to use on minukube registry
```bash
    docker tag ws-server-blue-green 127.0.0.1:5000/ws-server-blue-green
    docker tag ws-server-blue-green:0.0.1 127.0.0.1:5000/ws-server-blue-green:0.0.1
    docker tag ws-server-blue-green:latest 127.0.0.1:5000/ws-server-blue-green:latest
```

### Push to minukube registry
```bash
    docker push 127.0.0.1:5000/ws-server-blue-green:0.0.1
    docker push 127.0.0.1:5000/ws-server-blue-green:latest
```

### Install Chart on Kubernetes
```bash
    helm install ws-server-blue-green-helm ./ws-server-blue-green-helm
```

### Port Forward
```bash
    minikube service ws-server-blue-green-helm
```

# Update to green version

### Create a image
```bash
    docker build -t ws-server-blue-green:0.0.2 ./ws-server
```

### Tag image to use on minukube registry
```bash
    docker tag ws-server-blue-green 127.0.0.1:5000/ws-server-blue-green
    docker tag ws-server-blue-green:0.0.1 127.0.0.1:5000/ws-server-blue-green:0.0.2
    docker tag ws-server-blue-green:latest 127.0.0.1:5000/ws-server-blue-green:latest
```

### Push to minukube registry
```bash
    docker push 127.0.0.1:5000/ws-server-blue-green:0.0.2
    docker push 127.0.0.1:5000/ws-server-blue-green:latest
```

### Updating the chart
```bash
    helm upgrade ws-server-blue-green-helm ./ws-server-blue-green-helm
```

# To analyze the result

### Get pods
```bash
    kubectl get pods
```

### See the logs (windows)
```bash
    kubectl logs -f $(kubectl get pods | findstr ws-server-blue-green | ForEach-Object { ($_ -split '\s+')[0] })
```

# To clear everything

### Deleting the chart
```bash
    helm delete ws-server-blue-green-helm
```

### Deleting the images (windows)

```bash
docker rmi $(docker images | findstr ws-server-blue-green | ForEach-Object { ($_ -split '\s+')[2] }) --force
```