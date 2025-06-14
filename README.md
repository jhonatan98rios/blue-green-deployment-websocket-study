# How to run

### Start minikube
```bash
    minikube start
```

### Enable minikube container registry as principal while using the terminal (you'll need to re-run after opening a new terminal)
```bash
    # For Windows
    minikube addons enable registry minikube docker-env
    minikube -p minikube docker-env --shell powershell | Invoke-Expression

    # For linux
    minikube addons enable registry minikube docker-env
    eval $(minikube -p minikube docker-env)
```

### Adding bitnami helm repo
```bash
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
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
    docker tag ws-server-blue-green:0.0.1 127.0.0.1:5000/ws-server-blue-green:0.0.1
    docker tag ws-server-blue-green:0.0.1 127.0.0.1:5000/ws-server-blue-green:latest
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

---

# Update to green version

### Create a image
```bash
    docker build -t ws-server-blue-green:0.0.2 ./ws-server
```

### Tag image to use on minukube registry
```bash
    docker tag ws-server-blue-green:0.0.2 127.0.0.1:5000/ws-server-blue-green:0.0.2
    docker tag ws-server-blue-green:0.0.2 127.0.0.1:5000/ws-server-blue-green:latest
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

---

# To analyze the result

### Get pods
```bash
    kubectl get pods
```

### See the logs
```bash
    # Windows
    kubectl logs -f $(kubectl get pods | findstr ws-server-blue-green | ForEach-Object { ($_ -split '\s+')[0] })

    # Linux
    kubectl logs -f $(kubectl get pods --no-headers | grep ws-server-blue-green | awk '{print $1}')
```

---

# To clear everything

### Deleting the chart
```bash
    helm delete ws-server-blue-green-helm
```

### Deleting the images 

```bash
    # Windows
    docker rmi $(docker images | findstr ws-server-blue-green | ForEach-Object { ($_ -split '\s+')[2] }) --force

    # Linux
    docker rmi $(docker images | grep ws-server-blue-green | awk '{print $3}') --force

```