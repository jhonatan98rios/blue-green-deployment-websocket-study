# Running the Blue version

### Build, tag and push the blue image

```bash
docker build -t ws-server-blue-green:0.0.1 ./ws-server
docker tag ws-server-blue-green:0.0.1 127.0.0.1:5000/ws-server-blue-green:latest
docker push 127.0.0.1:5000/ws-server-blue-green:latest
```

### Installing the chart

```bash
helm install ws-server-blue-green-helm ./ws-server-blue-green-helm
```

### Expose the port (minikube only)

```bash
minikube service ws-server-blue-green-helm
```

---

# Updating to the Green version

### Build, tag and push the green image

```bash
docker build -t ws-server-blue-green:0.0.2 ./ws-server

docker tag ws-server-blue-green:0.0.2 ws-server-blue-green:latest
docker tag ws-server-blue-green:0.0.2 127.0.0.2:5000/ws-server-blue-green:0.0.2
docker tag ws-server-blue-green:latest 127.0.0.2:5000/ws-server-blue-green:latest

docker push 127.0.0.2:5000/ws-server-blue-green:0.0.2
docker push 127.0.0.2:5000/ws-server-blue-green:latest
```

### Updating the chart

```bash
helm upgrade ws-server-blue-green-helm ./ws-server-blue-green-helm
```

### Scaling up the replicas for rollout

```bash
kubectl scale deployment ws-server-blue-green-helm --replicas=2
```

# Deleting the chart

```bash
helm delete ws-server-blue-green-helm
```