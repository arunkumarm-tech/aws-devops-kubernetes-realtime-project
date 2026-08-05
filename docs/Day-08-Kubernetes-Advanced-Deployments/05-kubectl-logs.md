# `kubectl logs`

## Objective

Read Flask startup logs, follow new output, generate HTTP requests, and connect an application response to the Pod that handled it.

## Selecting a Pod

```bash
POD_NAME=$(kubectl get pods -n arun-devops \
  -l app=arun-flask \
  -o jsonpath='{.items[0].metadata.name}')

echo "$POD_NAME"
kubectl logs -n arun-devops "$POD_NAME"
```

One selected Pod was:

```text
arun-flask-deployment-6d8c958999-bb78m
```

Its startup log included:

```text
Serving Flask app 'app'
Debug mode: off
WARNING: This is a development server.
Running on all addresses (0.0.0.0)
Running on http://127.0.0.1:5000
Running on http://10.244.0.19:5000
```

`127.0.0.1` is loopback inside that Pod's network namespace. `10.244.0.19` was the Pod IP. The two lines do not mean two Flask servers were running; Flask was advertising ways the same listener could be addressed.

## Following live traffic

In one terminal:

```bash
kubectl port-forward -n arun-devops \
  service/arun-flask-service 8081:80
```

In a second terminal, logs were followed for the Pod identified in the application's hostname response:

```bash
kubectl logs -f -n arun-devops \
  arun-flask-deployment-6d8c958999-xlbp7
```

Requests were then generated:

```bash
curl http://localhost:8081
curl http://localhost:8081/health
```

The application returned its hostname and a healthy response. The log stream showed:

```text
"GET / HTTP/1.1" 200
"GET /health HTTP/1.1" 200
```

This connected the complete path:

```text
curl -> local port 8081 -> Service port 80
     -> selected Pod port 5000 -> Flask access log
```

## Shell-variable problem

The first live-log attempt in a second terminal failed:

```text
error: You must provide one or more resources by argument or filename.
```

`$POD_NAME` was empty because shell variables are local to the shell session in which they were set. Recreating the variable in the second terminal or using the exact Pod name fixed the issue.

The label query selects the first matching Pod, which is not necessarily the Pod that handled a particular request. The hostname included in this application's response made exact correlation possible.

## Useful variants

```bash
# Tail recent lines
kubectl logs -n arun-devops "$POD_NAME" --tail=100

# Include timestamps
kubectl logs -n arun-devops "$POD_NAME" --timestamps

# Logs from the previous terminated container instance
kubectl logs -n arun-devops "$POD_NAME" --previous

# Specify a container in a multi-container Pod
kubectl logs -n arun-devops "$POD_NAME" -c arun-flask-container
```

`--previous` is useful only when a previous container instance exists, typically after a restart. It was discussed but no restarted container was present in the final Pod (`Restart Count: 0`).

## Production boundary

`kubectl logs` is effective for a focused investigation but not a complete logging platform. Pods are temporary, local log files rotate, and incidents may span many replicas. Production workloads normally emit structured logs to stdout/stderr and forward them to a centralized system with retention, search, access control, and correlation IDs.

