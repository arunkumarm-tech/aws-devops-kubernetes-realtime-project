# Day 7 - Kubernetes Fundamentals and Local Setup

## Project

**AWS DevOps Kubernetes Real-Time Project**

---

## 1. Objective

The objective of Day 7 is to deploy the Jenkins-built Flask Docker image to a local Kubernetes cluster and understand the Kubernetes objects that keep the application available.

By the end of this session, the following activities were completed:

- Enabled and verified Kubernetes in Docker Desktop.
- Verified the local Kubernetes cluster and context.
- Created the `arun-devops` namespace.
- Created a Kubernetes Deployment with two Flask application Pods.
- Created a NodePort Service to provide stable access to the Pods.
- Tested the application through port-forwarding.
- Tested Service discovery and load balancing from inside the cluster.
- Scaled the Deployment from two Pods to three Pods.
- Demonstrated self-healing by deleting a managed Pod.
- Learned how Kubernetes connects the existing GitHub, Jenkins, Docker, and Amazon ECR workflow.

---

## 2. Day 7 Architecture Overview

### Complete DevOps Flow

```text
Developer
    |
    | git push
    v
GitHub Repository
    |
    | source checkout
    v
Jenkins CI Pipeline
    |
    | docker build
    v
Docker Image: arun-jenkins-flask-app:v1
    |
    | local image or image registry
    v
Docker Desktop Kubernetes Cluster
    |
    v
Namespace: arun-devops
    |
    v
Deployment: arun-flask-deployment
    |
    v
ReplicaSet
    |
    +-------------------+-------------------+
    |                   |                   |
    v                   v                   v
Flask Pod 1         Flask Pod 2         Flask Pod 3
    |                   |                   |
    +-------------------+-------------------+
                        |
                        v
          Service: arun-flask-service
                        |
                        v
             Browser / curl / Client
```

The third Pod appears after the scaling exercise. The initial Deployment contains two Pods.

### Request Flow

```text
Client request
      |
      v
localhost port-forward or NodePort
      |
      v
arun-flask-service
      |
      | selector: app=arun-flask
      v
One healthy Flask Pod
      |
      v
Flask application on container port 5000
```

---

## 3. How Git, GitHub, Jenkins, Docker, ECR, and Kubernetes Work Together

| Component | Responsibility | Role in This Project |
|---|---|---|
| Git | Tracks file changes and versions | Tracks application, Docker, Jenkins, and Kubernetes files |
| GitHub | Hosts the source repository | Provides the source code to Jenkins and the team |
| Jenkins | Automates continuous integration | Pulls the code, builds the image, and pushes it to Amazon ECR |
| Dockerfile | Defines the application runtime | Packages Flask and its dependencies into an image |
| Docker | Builds and runs containers | Built `arun-jenkins-flask-app:v1` and makes it available locally |
| Amazon ECR | Stores private container images | Stores versioned images for remote or EKS deployments |
| Kubernetes | Orchestrates containers | Creates, exposes, scales, and repairs Flask Pods |
| Docker Desktop | Provides the local runtime and cluster | Runs the Docker engine and the local Kubernetes control plane/nodes |

### Local Day 7 Image Flow

The Deployment uses:

```yaml
image: arun-jenkins-flask-app:v1
imagePullPolicy: IfNotPresent
```

`IfNotPresent` tells Kubernetes to use the image already available to the local container runtime when possible. If the image is not available, Kubernetes attempts to pull it from a configured registry.

> Docker Desktop versions can use different internal container runtimes. The reliable verification is the Pod status and events, not an assumption about image sharing. If a Pod reports `ImagePullBackOff`, push the image to a registry and update the Deployment to use the full registry URI.

### Production/EKS Image Flow

```text
GitHub -> Jenkins -> Docker Build -> Amazon ECR -> Amazon EKS -> Kubernetes Pods
```

For Amazon EKS, the image value normally uses the complete ECR URI:

```text
<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/arun-jenkins-flask-app:<IMAGE_TAG>
```

---

## 4. What Was Built on Day 7

| Kubernetes Object | Name | Purpose |
|---|---|---|
| Context | `docker-desktop` | Selects the local Docker Desktop cluster |
| Namespace | `arun-devops` | Isolates the project resources |
| Deployment | `arun-flask-deployment` | Declares the desired application state |
| ReplicaSet | Automatically generated | Maintains the requested number of Pods |
| Pods | Automatically generated | Run the Flask containers |
| Service | `arun-flask-service` | Provides stable networking and load balancing |
| Label | `app: arun-flask` | Connects the Deployment Pods to the Service |

Project files:

```text
kubernetes/
├── flask-deployment.yaml
└── flask-service.yaml
```

---

## 5. Kubernetes Fundamentals

### 5.1 Cluster

A Kubernetes cluster is a group of machines managed as one platform. It contains a control plane and one or more worker nodes. Docker Desktop provides a local single-node cluster suitable for learning and development.

### 5.2 Control Plane

The control plane manages the cluster's desired state.

| Component | Responsibility |
|---|---|
| API Server | Receives and validates Kubernetes API requests |
| etcd | Stores cluster configuration and state |
| Scheduler | Selects a node for each unscheduled Pod |
| Controller Manager | Runs controllers that reconcile actual state with desired state |

### 5.3 Worker Node

A worker node runs application workloads.

| Component | Responsibility |
|---|---|
| kubelet | Ensures assigned Pods and containers are running |
| Container runtime | Creates and runs containers |
| kube-proxy/networking | Implements Service networking rules |

### 5.4 Namespace

A namespace is a logical boundary inside a cluster. It helps organize resources, avoid naming conflicts, and apply access controls or resource quotas.

Real-world example:

```text
Cluster
├── dev namespace
├── test namespace
└── production namespace
```

This project uses:

```text
arun-devops
```

Resources in different namespaces may use the same name. Namespaces do not automatically provide complete network isolation; NetworkPolicies are needed when network isolation is required.

### 5.5 Pod

A Pod is the smallest deployable Kubernetes unit. It contains one or more closely related containers that share networking and storage. Pods are temporary and should not normally be created or depended on directly by name.

### 5.6 ReplicaSet

A ReplicaSet continuously maintains a specified number of identical Pod replicas. In this project, the Deployment automatically creates and owns the ReplicaSet.

### 5.7 Deployment

A Deployment manages ReplicaSets and provides declarative updates, scaling, rollout history, and rollback support. The project Deployment initially requests two replicas.

### 5.8 Service

A Service gives a changing set of Pods a stable virtual IP and DNS name. It finds Pods through labels and distributes connections across ready endpoints.

### Deployment vs ReplicaSet vs Pod vs Service

| Object | Main Job | Created/Managed By | Stable Identity? |
|---|---|---|---|
| Deployment | Manages releases and desired replica count | User/GitOps pipeline | Stable API object |
| ReplicaSet | Maintains the requested Pods | Deployment | Stable while revision exists |
| Pod | Runs the application container | ReplicaSet | No; replaceable |
| Service | Provides stable discovery and traffic routing | User/GitOps pipeline | Stable virtual IP and DNS |

---

## 6. Docker Desktop and Kubernetes Local Setup

### Enable Kubernetes

1. Open Docker Desktop.
2. Open **Settings**.
3. Select **Kubernetes**.
4. Enable Kubernetes and apply the change.
5. Wait until Docker Desktop reports that Kubernetes is running.

### Verify kubectl

```bash
kubectl version --client
```

### Verify the Context and Cluster

```bash
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl cluster-info
kubectl get nodes
```

Expected node status:

```text
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   ...   ...
```

The version and age values depend on the installed Docker Desktop release.

---

## 7. Namespace Creation and Verification

Create the namespace:

```bash
kubectl create namespace arun-devops
```

Verify it:

```bash
kubectl get namespaces
kubectl get namespace arun-devops
```

Expected status:

```text
NAME          STATUS   AGE
arun-devops   Active   ...
```

Optional: make the namespace the default for the current context:

```bash
kubectl config set-context --current --namespace=arun-devops
```

The documentation continues to use `-n arun-devops` explicitly so every command clearly shows its target namespace.

---

## 8. Kubernetes Deployment YAML

File: `kubernetes/flask-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: arun-flask-deployment
  namespace: arun-devops
spec:
  replicas: 2
  selector:
    matchLabels:
      app: arun-flask
  template:
    metadata:
      labels:
        app: arun-flask
    spec:
      containers:
        - name: arun-flask-container
          image: arun-jenkins-flask-app:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
```

### Line-by-Line Explanation

| YAML Field | Explanation |
|---|---|
| `apiVersion: apps/v1` | Uses the stable Kubernetes API group for Deployments |
| `kind: Deployment` | Creates a Deployment object |
| `metadata:` | Starts identifying information for the object |
| `name: arun-flask-deployment` | Assigns the Deployment name |
| `namespace: arun-devops` | Creates the Deployment inside the project namespace |
| `spec:` | Starts the desired-state specification |
| `replicas: 2` | Requests two running application Pods |
| `selector:` | Defines which Pods the Deployment owns |
| `matchLabels:` | Selects Pods using exact labels |
| `app: arun-flask` | Ownership selector used by the Deployment |
| `template:` | Defines the blueprint for every new Pod |
| `template.metadata.labels:` | Applies labels to Pods created from the template |
| `app: arun-flask` | Makes the Pod label match the Deployment and Service selectors |
| `template.spec:` | Starts the Pod runtime configuration |
| `containers:` | Lists containers in the Pod |
| `name: arun-flask-container` | Names the Flask container |
| `image: arun-jenkins-flask-app:v1` | Selects the Docker image and tag to run |
| `imagePullPolicy: IfNotPresent` | Reuses a local image if available; otherwise attempts a pull |
| `ports:` | Documents ports exposed by the container |
| `containerPort: 5000` | Declares that Flask listens on port 5000 inside the Pod |

### Why the Two Labels Must Match

These values must match:

```yaml
selector:
  matchLabels:
    app: arun-flask

template:
  metadata:
    labels:
      app: arun-flask
```

The Deployment selector identifies the Pods it manages. Kubernetes rejects a Deployment whose selector does not match its Pod template labels.

### Apply and Verify the Deployment

```bash
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl get deployments -n arun-devops
kubectl get replicasets -n arun-devops
kubectl get pods -n arun-devops
kubectl get pods -n arun-devops -o wide
```

Expected Deployment state:

```text
NAME                    READY   UP-TO-DATE   AVAILABLE
arun-flask-deployment   2/2     2            2
```

Pod suffixes are automatically generated and will differ on every system.

---

## 9. Kubernetes Service YAML

File: `kubernetes/flask-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: arun-flask-service
  namespace: arun-devops
spec:
  selector:
    app: arun-flask
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: NodePort
```

### Line-by-Line Explanation

| YAML Field | Explanation |
|---|---|
| `apiVersion: v1` | Uses the core Kubernetes API for Services |
| `kind: Service` | Creates a Service object |
| `metadata:` | Starts identifying information |
| `name: arun-flask-service` | Sets the stable Service name and DNS prefix |
| `namespace: arun-devops` | Places the Service with the application |
| `spec:` | Starts the Service configuration |
| `selector:` | Defines which Pods receive traffic |
| `app: arun-flask` | Selects Pods labeled `app=arun-flask` |
| `ports:` | Lists ports provided by the Service |
| `protocol: TCP` | Uses TCP for application traffic |
| `port: 80` | Exposes port 80 on the Service virtual IP |
| `targetPort: 5000` | Forwards traffic to Flask port 5000 in a selected Pod |
| `type: NodePort` | Also exposes the Service on a port assigned to each node |

Because `nodePort` is not manually specified, Kubernetes assigns an available port, normally from the configured NodePort range.

### Port Mapping

```text
Client -> NodePort <assigned-port> -> Service port 80 -> Pod targetPort 5000
```

### Apply and Verify the Service

```bash
kubectl apply -f kubernetes/flask-service.yaml
kubectl get services -n arun-devops
kubectl describe service arun-flask-service -n arun-devops
kubectl get endpoints arun-flask-service -n arun-devops
```

Expected Service pattern:

```text
NAME                 TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)
arun-flask-service   NodePort   <cluster-ip>    <none>        80:<node-port>/TCP
```

The endpoints should contain one Pod IP for each ready matching Pod.

---

## 10. Labels and Selectors

Labels are key/value metadata attached to Kubernetes objects. Selectors query or connect objects by those labels.

This project uses:

```yaml
app: arun-flask
```

The relationship is:

```text
Deployment selector: app=arun-flask
        |
        v
Pod labels: app=arun-flask
        ^
        |
Service selector: app=arun-flask
```

Useful verification commands:

```bash
kubectl get pods -n arun-devops --show-labels
kubectl get pods -n arun-devops -l app=arun-flask
kubectl get endpoints arun-flask-service -n arun-devops
```

If the Service selector does not match the Pod label, the Service exists but has no application endpoints.

---

## 11. What Happens Internally After `kubectl apply`

### Deployment Flow

| Step | Internal Action |
|---|---|
| 1 | `kubectl` reads and validates the local YAML structure |
| 2 | `kubectl` sends the desired object to the API Server |
| 3 | The API Server authenticates, authorizes, validates, and stores state in etcd |
| 4 | The Deployment controller notices the new desired state |
| 5 | The Deployment controller creates a ReplicaSet |
| 6 | The ReplicaSet controller creates two Pod objects |
| 7 | The Scheduler assigns each unscheduled Pod to a node |
| 8 | The node's kubelet observes the assigned Pods |
| 9 | The container runtime obtains the image and starts the containers |
| 10 | Networking gives each Pod its own cluster IP address |
| 11 | Pod status is reported back through the API Server |
| 12 | Controllers continue reconciling until desired and actual state match |

### Service Flow

| Step | Internal Action |
|---|---|
| 1 | The Service is stored through the API Server |
| 2 | Kubernetes finds ready Pods whose labels match `app=arun-flask` |
| 3 | EndpointSlice data is created or updated for those Pod IPs |
| 4 | Cluster networking installs routing/load-balancing rules |
| 5 | Cluster DNS creates a record for the Service name |
| 6 | Connections to the Service are forwarded to a ready endpoint |

Kubernetes uses continuous reconciliation. It does not perform these actions only once; controllers keep checking and correcting the cluster state.

---

## 12. Port-Forwarding Explained

Command:

```bash
kubectl port-forward service/arun-flask-service 8081:80 -n arun-devops
```

Test in another terminal:

```bash
curl http://localhost:8081
curl http://localhost:8081/health
open http://localhost:8081
```

### Apartment and Tunnel Analogy

Think of the Kubernetes cluster as a secured apartment building:

- The Service is the reception desk.
- Each Pod is an apartment containing a Flask application.
- Port 80 is the reception desk's extension.
- Port 5000 is the application door inside each apartment.
- `kubectl port-forward` creates a temporary private tunnel from your laptop to reception.

```text
Laptop localhost:8081
        |
        | temporary tunnel
        v
Service port 80
        |
        v
Selected Pod port 5000
```

Port-forwarding is ideal for local testing and debugging. It is temporary, runs while the command is active, and is not a production exposure method.

Press `Control+C` in the port-forward terminal to stop the tunnel.

---

## 13. Service DNS and In-Cluster Communication

The Service DNS names are:

```text
arun-flask-service
arun-flask-service.arun-devops
arun-flask-service.arun-devops.svc.cluster.local
```

The short name works for a client in the same namespace. The namespace-qualified or fully qualified name is safer across namespaces.

Create a temporary curl client inside the project namespace:

```bash
kubectl run curl-test \
  --image=curlimages/curl \
  --restart=Never \
  -n arun-devops \
  --command -- sleep 3600
```

Wait for it to become ready:

```bash
kubectl wait --for=condition=Ready pod/curl-test -n arun-devops --timeout=60s
```

Call the Service:

```bash
kubectl exec -n arun-devops curl-test -- curl http://arun-flask-service
kubectl exec -n arun-devops curl-test -- curl http://arun-flask-service/health
```

Clean up the test Pod:

```bash
kubectl delete pod curl-test -n arun-devops
```

---

## 14. Service Load Balancing

The Service distributes new network connections across ready Pod endpoints. It does not guarantee strict round-robin output for every application request.

Run repeated requests from inside the cluster:

```bash
for i in {1..10}; do
  kubectl exec -n arun-devops curl-test -- \
    curl -s http://arun-flask-service
  echo
done
```

If the Flask response includes the container hostname, different Pod names demonstrate that multiple backends are serving requests.

### Why `localhost` May Appear to Reach Only One Pod

- A port-forward connection can remain attached to one selected backend for the lifetime of that connection.
- HTTP connection reuse can send multiple requests through the same established connection.
- Load balancing operates on connections and is not a promise that responses alternate perfectly.
- The `curl-test` Pod uses normal in-cluster Service networking, making backend distribution easier to observe over multiple new connections.

To inspect the actual backends directly:

```bash
kubectl get endpoints arun-flask-service -n arun-devops
kubectl get endpointslices -n arun-devops -l kubernetes.io/service-name=arun-flask-service
```

---

## 15. Scaling from Two Pods to Three Pods

Initial desired state:

```yaml
replicas: 2
```

Scale using an imperative command:

```bash
kubectl scale deployment arun-flask-deployment \
  --replicas=3 \
  -n arun-devops
```

Watch the new Pod start:

```bash
kubectl get pods -n arun-devops -w
```

Verify the result:

```bash
kubectl get deployment arun-flask-deployment -n arun-devops
kubectl get pods -n arun-devops -l app=arun-flask
kubectl get endpoints arun-flask-service -n arun-devops
```

Expected Deployment state:

```text
arun-flask-deployment   3/3   3   3
```

Press `Control+C` to stop watch mode.

### Declarative State Warning

`kubectl scale` changes the live Deployment to three replicas, but the repository YAML still says `replicas: 2`. A future `kubectl apply -f kubernetes/flask-deployment.yaml` will restore two replicas.

For a permanent Git-managed change, update `replicas` in the YAML to `3`, review the diff, and commit it.

---

## 16. Self-Healing Demonstration

List the managed Pods:

```bash
kubectl get pods -n arun-devops -l app=arun-flask
```

Delete one generated Pod using its real name:

```bash
kubectl delete pod <POD_NAME> -n arun-devops
```

Watch the replacement:

```bash
kubectl get pods -n arun-devops -w
```

What happens internally:

1. The selected Pod is deleted.
2. The ReplicaSet observes that actual replicas are below the desired count.
3. The ReplicaSet immediately creates a replacement Pod.
4. The Scheduler assigns the new Pod to a node.
5. The kubelet starts the container.
6. When ready, the new Pod becomes a Service endpoint.

The replacement Pod has a new name and IP address. The Service name remains unchanged, so clients do not need to track individual Pods.

---

## 17. Every Command Used on Day 7

> Run these commands from the repository root. Dynamic placeholders such as `<POD_NAME>` and `<node-port>` must be replaced with values from your cluster.

### Environment Verification

```bash
docker --version
docker images | grep arun-jenkins-flask-app
kubectl version --client
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl cluster-info
kubectl get nodes
```

### Namespace

```bash
kubectl create namespace arun-devops
kubectl get namespaces
kubectl get namespace arun-devops
```

### Deployment

```bash
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl get deployments -n arun-devops
kubectl get replicasets -n arun-devops
kubectl get pods -n arun-devops
kubectl get pods -n arun-devops -o wide
kubectl get pods -n arun-devops --show-labels
kubectl describe deployment arun-flask-deployment -n arun-devops
kubectl describe pod <POD_NAME> -n arun-devops
kubectl logs <POD_NAME> -n arun-devops
```

### Service and Application Testing

```bash
kubectl apply -f kubernetes/flask-service.yaml
kubectl get services -n arun-devops
kubectl describe service arun-flask-service -n arun-devops
kubectl get endpoints arun-flask-service -n arun-devops
kubectl port-forward service/arun-flask-service 8081:80 -n arun-devops
curl http://localhost:8081
curl http://localhost:8081/health
open http://localhost:8081
```

### Service DNS and Load Balancing

```bash
kubectl run curl-test --image=curlimages/curl --restart=Never -n arun-devops --command -- sleep 3600
kubectl wait --for=condition=Ready pod/curl-test -n arun-devops --timeout=60s
kubectl exec -n arun-devops curl-test -- curl http://arun-flask-service
kubectl exec -n arun-devops curl-test -- curl http://arun-flask-service/health
kubectl get endpointslices -n arun-devops -l kubernetes.io/service-name=arun-flask-service
kubectl delete pod curl-test -n arun-devops
```

### Scaling and Self-Healing

```bash
kubectl scale deployment arun-flask-deployment --replicas=3 -n arun-devops
kubectl get pods -n arun-devops -w
kubectl get deployment arun-flask-deployment -n arun-devops
kubectl delete pod <POD_NAME> -n arun-devops
kubectl get pods -n arun-devops -w
kubectl rollout status deployment/arun-flask-deployment -n arun-devops
```

### General Troubleshooting

```bash
kubectl get all -n arun-devops
kubectl get events -n arun-devops --sort-by=.metadata.creationTimestamp
kubectl logs <POD_NAME> -n arun-devops
kubectl logs <POD_NAME> -n arun-devops --previous
kubectl describe pod <POD_NAME> -n arun-devops
kubectl rollout history deployment/arun-flask-deployment -n arun-devops
```

---

## 18. Troubleshooting Scenarios

### Scenario 1: `kubectl` Cannot Connect to the Cluster

Typical message:

```text
The connection to the server ... was refused
```

Checks and fix:

```bash
kubectl config current-context
kubectl config use-context docker-desktop
kubectl cluster-info
```

Ensure Docker Desktop is running and Kubernetes is enabled and ready.

### Scenario 2: Namespace Not Found

Typical message:

```text
namespaces "arun-devops" not found
```

Fix:

```bash
kubectl create namespace arun-devops
```

### Scenario 3: `ImagePullBackOff` or `ErrImagePull`

Possible causes:

- The local image is unavailable to the Kubernetes runtime.
- The image name or tag is incorrect.
- The registry is private and authentication is missing.
- The ECR login/permissions or image URI is incorrect.

Diagnosis:

```bash
kubectl describe pod <POD_NAME> -n arun-devops
docker images | grep arun-jenkins-flask-app
```

Fix options:

- Build the exact local image and tag.
- Push the image to Amazon ECR and use its complete URI.
- Configure the required registry authentication.
- Correct the image tag and reapply the Deployment.

### Scenario 4: `CrashLoopBackOff`

The container starts and repeatedly exits.

Diagnosis:

```bash
kubectl logs <POD_NAME> -n arun-devops
kubectl logs <POD_NAME> -n arun-devops --previous
kubectl describe pod <POD_NAME> -n arun-devops
```

Check application exceptions, missing environment variables, dependencies, and the container startup command.

### Scenario 5: Pod Is `Pending`

Diagnosis:

```bash
kubectl describe pod <POD_NAME> -n arun-devops
kubectl get events -n arun-devops --sort-by=.metadata.creationTimestamp
```

Common causes include insufficient CPU/memory, scheduling restrictions, or unavailable storage.

### Scenario 6: Service Has No Endpoints

Check:

```bash
kubectl get pods -n arun-devops --show-labels
kubectl get endpoints arun-flask-service -n arun-devops
```

Confirm the Service selector is `app: arun-flask`, the Pods have the same label, and the Pods are ready.

### Scenario 7: Port-Forward Fails

Possible causes include an incorrect resource name, namespace, local port conflict, or no ready Pod.

```bash
kubectl get service arun-flask-service -n arun-devops
kubectl get pods -n arun-devops
kubectl port-forward service/arun-flask-service 8082:80 -n arun-devops
```

Use a different local port such as `8082` if `8081` is already in use.

### Scenario 8: `localhost:<node-port>` Does Not Work on Docker Desktop

NodePort behavior can vary with the desktop networking environment. Verify the Service and use port-forwarding for a predictable local test:

```bash
kubectl get service arun-flask-service -n arun-devops
kubectl port-forward service/arun-flask-service 8081:80 -n arun-devops
```

### Scenario 9: YAML Validation or Indentation Error

```bash
kubectl apply --dry-run=client -f kubernetes/flask-deployment.yaml
kubectl apply --dry-run=client -f kubernetes/flask-service.yaml
```

YAML uses spaces for indentation. Do not use tabs.

### Scenario 10: Changes Do Not Appear in the Pods

Using the same mutable image tag may leave existing Pods running an older image. Prefer unique tags such as a Jenkins build number or Git commit SHA, update the Deployment, and verify the rollout:

```bash
kubectl rollout status deployment/arun-flask-deployment -n arun-devops
kubectl rollout history deployment/arun-flask-deployment -n arun-devops
```

### Scenario 11: Wrong Namespace Shows No Resources

```bash
kubectl get pods -A
kubectl get all -n arun-devops
```

Always include the correct namespace or set it explicitly on the current context.

### Scenario 12: Deployment Is Not Reaching Ready State

```bash
kubectl describe deployment arun-flask-deployment -n arun-devops
kubectl get replicasets -n arun-devops
kubectl get events -n arun-devops --sort-by=.metadata.creationTimestamp
```

Follow the failure from Deployment to ReplicaSet to Pod, then inspect Pod events and logs.

---

## 19. Important Kubernetes Best Practices

- Use Deployments instead of creating standalone application Pods.
- Store manifests in Git and review every change.
- Use immutable image tags such as build numbers or Git commit SHAs.
- Configure CPU and memory requests and limits.
- Add readiness, liveness, and startup probes.
- Store secrets in a proper secret manager; never commit plaintext credentials.
- Use ConfigMaps for non-sensitive configuration.
- Apply least-privilege RBAC.
- Use separate namespaces and access policies for environments.
- Add NetworkPolicies where supported.
- Use rolling updates and verify rollout status.
- Configure a production ingress or load balancer rather than port-forwarding.
- Scan images and manifests for vulnerabilities and misconfiguration.
- Monitor Pods, application metrics, logs, and cluster events.
- Use multiple nodes and replicas for production high availability.

---

## 20. Interview Questions and Answers

### Q1: What is Kubernetes?

Kubernetes is a container orchestration platform that automates application deployment, scaling, networking, and recovery across a cluster.

### Q2: Why use Kubernetes when Docker already runs containers?

Docker packages and runs individual containers. Kubernetes coordinates many containers across nodes and provides desired-state management, service discovery, scaling, rolling updates, and self-healing.

### Q3: What is a Kubernetes cluster?

A cluster is a control plane plus one or more worker nodes that run and manage containerized workloads.

### Q4: What does the API Server do?

It is the entry point to the Kubernetes API. It validates requests, enforces authentication and authorization, and persists cluster state.

### Q5: What is etcd?

etcd is the distributed key-value store that holds Kubernetes cluster state and configuration.

### Q6: What does the Scheduler do?

The Scheduler selects a suitable node for each unscheduled Pod based on resources, constraints, affinity, taints, and other policies.

### Q7: What is a Pod?

A Pod is the smallest deployable Kubernetes unit and runs one or more closely related containers with shared networking and storage.

### Q8: Why should an application not depend on a Pod IP?

Pods are replaceable. Their names and IP addresses can change after scaling, failure, or rollout, so clients should use a Service.

### Q9: What is a Deployment?

A Deployment manages ReplicaSets and supports declarative replicas, rolling updates, rollout history, scaling, and rollback.

### Q10: What is a ReplicaSet?

A ReplicaSet continuously ensures that the desired number of matching Pods exists.

### Q11: What is a Service?

A Service provides a stable virtual IP and DNS name for a selected group of Pods and routes traffic to ready endpoints.

### Q12: What is a namespace?

A namespace logically groups cluster resources and provides a scope for names, permissions, quotas, and policies.

### Q13: What are labels and selectors?

Labels are key/value metadata. Selectors find objects with particular labels and connect Deployments and Services to Pods.

### Q14: Why must the Deployment selector match the Pod template label?

The selector defines which Pods the Deployment owns. Kubernetes requires it to match the labels on Pods generated from the template.

### Q15: How does the Service find the Flask Pods?

Its selector `app=arun-flask` matches the same label on the Deployment's Pods. Kubernetes publishes the ready matching Pod IPs as endpoints.

### Q16: What is the difference between `port`, `targetPort`, and `nodePort`?

`port` is the Service port, `targetPort` is the destination port in the Pod, and `nodePort` is the externally reachable port opened on cluster nodes for a NodePort Service.

### Q17: What is a ClusterIP Service?

ClusterIP is the default Service type. It exposes the application through an internal cluster virtual IP.

### Q18: What is a NodePort Service?

NodePort exposes a Service on a port on each node in addition to its ClusterIP, mainly for simple access and testing.

### Q19: What is a LoadBalancer Service?

It asks a supported infrastructure provider to provision an external load balancer that routes to the Kubernetes Service.

### Q20: What is port-forwarding?

Port-forwarding creates a temporary connection from a local port to a Pod or Service port for development and debugging.

### Q21: Is port-forwarding suitable for production traffic?

No. Production applications normally use an Ingress, Gateway, or LoadBalancer Service with security and high-availability controls.

### Q22: How does Service DNS work?

Cluster DNS resolves Service names such as `arun-flask-service.arun-devops` to the Service virtual IP for in-cluster clients.

### Q23: How did you demonstrate load balancing?

I created a temporary curl Pod and repeatedly called the Service DNS name. Responses containing different container hostnames showed that multiple ready Pods served connections.

### Q24: Why might repeated requests show the same Pod?

Connection reuse, persistent connections, or port-forward behavior can keep traffic on one backend. Kubernetes load balancing does not promise perfect response-by-response alternation.

### Q25: How do you scale a Deployment?

Use `kubectl scale deployment <name> --replicas=<count>` or change the replica count declaratively in the manifest and apply it.

### Q26: What is self-healing in Kubernetes?

Controllers continuously compare desired and actual state. If a managed Pod disappears, the ReplicaSet creates a replacement.

### Q27: What happens after deleting one Deployment-managed Pod?

The ReplicaSet detects a replica shortage, creates a new Pod, the Scheduler assigns it, and the kubelet starts its container.

### Q28: What does `imagePullPolicy: IfNotPresent` mean?

Kubernetes uses an image already present on the node when available and otherwise attempts to pull it.

### Q29: What causes `ImagePullBackOff`?

Common causes include an invalid image name/tag, unavailable image, private registry authentication failure, network failure, or missing registry permissions.

### Q30: How do you troubleshoot `CrashLoopBackOff`?

Inspect current and previous container logs, describe the Pod, review events, and validate configuration, dependencies, and startup commands.

### Q31: What is the difference between desired state and actual state?

Desired state is the configuration declared to Kubernetes. Actual state is what currently exists. Controllers reconcile actual state toward desired state.

### Q32: What is a rolling update?

A rolling update gradually replaces old Pods with new Pods while maintaining application availability according to the Deployment strategy.

### Q33: How do you check a Deployment rollout?

Use `kubectl rollout status deployment/<name> -n <namespace>` and inspect `kubectl rollout history` when needed.

### Q34: How do you roll back a Deployment?

Use `kubectl rollout undo deployment/<name> -n <namespace>`, then verify its status and application health.

### Q35: Why use Amazon ECR with Kubernetes?

ECR securely stores versioned container images that Amazon EKS or another authorized Kubernetes environment can pull consistently.

### Q36: How should ECR access be secured in Amazon EKS?

Use IAM roles and least-privilege policies, keep nodes or workload identities authorized, and avoid embedding AWS access keys in manifests.

### Q37: What is the difference between readiness and liveness probes?

Readiness decides whether a Pod should receive Service traffic. Liveness detects an unhealthy container that should be restarted.

### Q38: Why configure resource requests and limits?

Requests help the Scheduler place Pods; limits prevent a container from consuming more than its allowed CPU or memory.

### Q39: Why use unique Docker image tags?

Unique tags provide traceability, predictable rollouts, simpler debugging, and reliable rollback to a known build.

### Q40: Explain the Day 7 implementation in an interview.

I enabled a local Docker Desktop Kubernetes cluster, created an isolated namespace, and deployed a Jenkins-built Flask image using a Deployment with two replicas. I exposed the Pods through a label-selected NodePort Service, verified the application through port-forwarding and Service DNS, demonstrated connection distribution from an in-cluster curl Pod, scaled the Deployment to three replicas, and proved self-healing by deleting a managed Pod and observing its automatic replacement.

---

## 21. Resume Points

- Deployed a containerized Flask application to a local Kubernetes cluster using declarative YAML manifests.
- Created and managed Kubernetes Namespaces, Deployments, ReplicaSets, Pods, and Services.
- Configured label selectors and a NodePort Service for stable discovery and traffic routing.
- Integrated the Kubernetes deployment stage with an existing GitHub, Jenkins, Docker, and Amazon ECR CI workflow.
- Validated application access through Kubernetes port-forwarding and in-cluster Service DNS.
- Demonstrated Service traffic distribution across multiple Flask Pods.
- Performed horizontal scaling from two to three application replicas.
- Demonstrated Kubernetes self-healing through automatic Pod replacement.
- Diagnosed workloads using Pod logs, descriptions, events, endpoints, and rollout commands.
- Applied container deployment practices including namespaces, immutable image tagging, health probes, resource controls, and least-privilege guidance.

---

## 22. Git Commands to Commit and Push Day 7

Review the working tree before staging:

```bash
cd /Users/arunkumarm/Projects/aws-devops-kubernetes-realtime-project

git status
git diff -- docs/Day7-Kubernetes-Fundamentals-and-Local-Setup.md
git diff --no-index /dev/null kubernetes/flask-deployment.yaml
git diff --no-index /dev/null kubernetes/flask-service.yaml
```

Stage only the three Day 7 files:

```bash
git add docs/Day7-Kubernetes-Fundamentals-and-Local-Setup.md \
  kubernetes/flask-deployment.yaml \
  kubernetes/flask-service.yaml
```

Verify the staged changes:

```bash
git diff --cached --check
git diff --cached --stat
git status
```

Commit and push:

```bash
git commit -m "Day 7: Add Kubernetes fundamentals and local setup"
git push origin main
git status
```

These commands intentionally stage only the Day 7 document and its two Kubernetes manifests, preserving any unrelated working-tree changes.

---

## 23. Day 7 Completion Checklist

- [x] Docker Desktop Kubernetes enabled
- [x] `kubectl` and cluster context verified
- [x] `arun-devops` namespace created
- [x] Deployment manifest created and explained
- [x] Two Flask replicas deployed
- [x] ReplicaSet and Pods verified
- [x] Service manifest created and explained
- [x] Labels and selectors verified
- [x] Application tested through port-forwarding
- [x] Service DNS tested from inside the cluster
- [x] Service load balancing demonstrated
- [x] Deployment scaled from two Pods to three Pods
- [x] Self-healing demonstrated by deleting a Pod
- [x] Troubleshooting commands documented
- [x] Interview questions and answers documented
- [x] Resume points documented
- [x] Day 7 documentation completed

### Final Outcome

Day 7 extended the project from a container image delivery workflow:

```text
GitHub -> Jenkins -> Docker Build -> Amazon ECR
```

to a Kubernetes application workflow:

```text
GitHub -> Jenkins -> Docker Image -> Kubernetes Deployment
                                      |
                                      v
                             ReplicaSet -> Pods
                                      |
                                      v
                              Kubernetes Service
```

```text
Status: DAY 7 COMPLETED SUCCESSFULLY
```

---

## 24. Day 8 Preview - Kubernetes Configuration and Production Readiness

Day 8 can build on this local foundation by adding:

- ConfigMaps for non-sensitive application configuration.
- Secrets for sensitive values without hardcoding them in images.
- Readiness, liveness, and startup probes.
- CPU and memory requests and limits.
- Rolling updates and rollback demonstrations.
- Environment-specific image tags and configuration.
- Ingress or Gateway-based HTTP routing.
- Preparation for deploying the same manifests to Amazon EKS.

The Day 7 local cluster proves the core orchestration workflow. Day 8 will make the workload safer, configurable, and closer to a production deployment.
