# ConfigMaps

## Objective

Move non-sensitive application settings out of the container image and inject them into the Flask Pods as environment variables.

## ConfigMap created

```bash
kubectl create configmap arun-flask-config \
  --from-literal=APP_ENV=development \
  --from-literal=APP_MESSAGE="Running from Kubernetes ConfigMap" \
  -n arun-devops

kubectl get configmap arun-flask-config \
  -n arun-devops \
  -o yaml
```

Observed data:

```yaml
data:
  APP_ENV: development
  APP_MESSAGE: Running from Kubernetes ConfigMap
```

Creating a ConfigMap does not change an application on its own. The Deployment's Pod template has to reference it.

## Deployment fragment used

The `env` block belongs under the container, aligned with `image`, `imagePullPolicy`, and `ports`:

```yaml
spec:
  containers:
    - name: arun-flask-container
      image: arun-jenkins-flask-app:v1
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 5000
      env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: arun-flask-config
              key: APP_ENV
        - name: APP_MESSAGE
          valueFrom:
            configMapKeyRef:
              name: arun-flask-config
              key: APP_MESSAGE
```

The first attempt placed `env` at the wrong indentation level. `kubectl apply` rejected the patch because `env` is not a valid field beside `containers`; it is a property of an individual container. After correcting the indentation:

```bash
kubectl apply -f kubernetes/flask-deployment.yaml

kubectl rollout status deployment/arun-flask-deployment \
  -n arun-devops
```

Observed output:

```text
deployment.apps/arun-flask-deployment configured
deployment "arun-flask-deployment" successfully rolled out
```

## Verification inside a Pod

```bash
POD_NAME=$(kubectl get pods -n arun-devops \
  -l app=arun-flask \
  -o jsonpath='{.items[0].metadata.name}')

kubectl exec -n arun-devops "$POD_NAME" -- env | grep APP_
```

Observed:

```text
APP_ENV=development
APP_MESSAGE=Running from Kubernetes ConfigMap
```

This was the useful proof. It established that the ConfigMap existed, the Deployment referenced the correct keys, replacement Pods were created from the new template, and the running container received the values.

## Update behavior

Environment variables are fixed when a container starts. Editing a ConfigMap does not update those environment variables inside already-running Pods. A controlled restart or a new Pod-template revision is needed. ConfigMap volumes have different refresh behavior, but the application must still reread the file.

## Production use

ConfigMaps are suitable for non-secret, environment-specific configuration such as log levels, feature flags, service URLs, and display messages. They are not a place for passwords or API keys. Keep configuration names and required keys stable, validate manifests before applying, and promote configuration through the same review process as application changes.

## Files involved

- Live object: `ConfigMap/arun-flask-config` in `arun-devops`
- Deployment edited during the exercise: `kubernetes/flask-deployment.yaml`

The live test succeeded, but the repository version inspected while preparing these notes still contained the earlier Day 7 container block. That manifest should be reconciled separately before it is treated as the source of truth.

