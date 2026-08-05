# Secrets

## Objective

Create database credentials as a namespaced Kubernetes Secret, reference its keys from the Deployment, and verify that the running container received them.

## What supplied the credentials

Kubernetes did not invent or discover a username and password. The values were supplied in the `kubectl create secret` command. In a company, credentials would normally be generated or approved by a database/security workflow and delivered through a controlled secrets system.

The project Secret was created in `arun-devops`:

```bash
kubectl create secret generic arun-flask-secret \
  --from-literal=DB_USERNAME=admin \
  --from-literal=DB_PASSWORD='<redacted>' \
  -n arun-devops
```

The password used during the practical appeared in terminal output and chat history. It is deliberately not repeated here and should not be reused. If it protects any real system, rotate it.

## Base64 is encoding, not encryption

```bash
kubectl get secret arun-flask-secret \
  -n arun-devops \
  -o yaml
```

The API returned Base64 strings under `data`. Anyone who can read the Secret can decode them. Kubernetes Secret objects mainly provide a distinct API type and access-control boundary; stronger protection depends on RBAC, etcd encryption at rest, audit controls, and an external secret-management process.

## Namespace lesson

An early `inventory-db-secret` was created without `-n arun-devops`, so it went to the current/default namespace. A second object with the same name was then created in `arun-devops`. These are separate objects because most Kubernetes resources are namespaced.

```bash
kubectl create secret generic inventory-db-secret \
  --from-literal=DB_USERNAME=inventory_app \
  --from-literal=DB_PASSWORD='<redacted>' \
  -n arun-devops
```

The unused demonstration Secret was later deleted. The incident reinforced a simple rule: specify the namespace on both creation and inspection commands.

## Deployment fragment used

```yaml
env:
  - name: DB_USERNAME
    valueFrom:
      secretKeyRef:
        name: arun-flask-secret
        key: DB_USERNAME
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: arun-flask-secret
        key: DB_PASSWORD
```

After saving the Deployment manifest, “apply it” meant sending that desired configuration to the Kubernetes API:

```bash
kubectl apply -f kubernetes/flask-deployment.yaml

kubectl rollout status deployment/arun-flask-deployment \
  -n arun-devops
```

Because the Pod template changed, the Deployment created replacement Pods.

## Verification

```bash
kubectl exec -n arun-devops "$POD_NAME" -- env | grep DB_
```

The command showed the expected `DB_USERNAME` and `DB_PASSWORD` variables. `kubectl describe pod` also confirmed that both came from `arun-flask-secret`, without printing their values.

## Production handling

- Do not commit Secret YAML containing real Base64 values.
- Do not print secrets with `env`, logs, screenshots, shell history, or CI output.
- Grant applications access only to the secrets they require.
- Enable Kubernetes encryption at rest and restrict Secret reads with RBAC.
- Prefer AWS Secrets Manager/Parameter Store plus an approved integration such as the Secrets Store CSI Driver or External Secrets Operator on EKS.
- Rotate credentials and support overlapping old/new credentials where zero-downtime rotation requires it.
- Remember that environment variables may be visible to processes and diagnostic tooling; mounted files can offer better rotation patterns in some applications.

For this learning exercise, printing the variables proved injection. It should not become the normal production validation method.

