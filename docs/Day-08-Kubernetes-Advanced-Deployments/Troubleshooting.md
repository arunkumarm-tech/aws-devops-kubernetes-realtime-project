# Day 8 Troubleshooting Record

These are issues encountered during the exercise, with the evidence used to diagnose them.

## Deployment apply rejected the YAML

**Symptom**

```text
The request is invalid: patch: Invalid value ...
```

**Cause**

`env` was aligned outside the container item. Kubernetes expects it beneath the container alongside `image` and `ports`.

**Fix**

Correct the indentation, inspect the file, validate it, then apply:

```bash
kubectl apply --dry-run=server -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl rollout status deployment/arun-flask-deployment -n arun-devops
```

**Lesson**

YAML can be syntactically valid while representing the wrong object shape. Validate against the Kubernetes API schema.

## Secret created in the wrong namespace

**Symptom**

`inventory-db-secret` was first created without a namespace and then appeared absent when working in `arun-devops`.

**Cause**

Omitting `-n arun-devops` used the current/default namespace. A Secret reference is namespace-scoped.

**Fix**

Create or inspect it with the explicit namespace and remove the unused demonstration object.

**Lesson**

Include `-n arun-devops` consistently or set and visibly verify a namespace in the current context.

## Replica count changed from three to two

**Symptom**

Day 7 ended with three Pods, but after applying the Day 8 manifest the Deployment reported `2/2`.

**Cause**

The earlier `kubectl scale --replicas=3` changed live state only. The file still declared `replicas: 2`, and `kubectl apply` restored that declared value.

**Fix**

Decide the intended count, update the manifest, review the diff, and apply it. Do not rely on an imperative change that source control contradicts.

**Lesson**

Git should describe the desired state. Live changes that are not written back create configuration drift.

## Literal `<pod-name>` executed

**Symptom**

```text
zsh: no such file or directory: pod-name
```

Subsequent commands showed Mac environment variables and a macOS resolver file.

**Cause**

Placeholder text was copied literally. The shell treated angle brackets as redirection, so `kubectl exec` never ran successfully.

**Fix**

Use the real Pod name or populate and verify `$POD_NAME` first.

**Lesson**

Confirm the prompt and runtime context before issuing diagnostic commands. `/app` and the container's files were reliable markers here.

## Pipe character typed as `¶`

**Symptom**

```text
env: '\302': No such file or directory
```

**Cause**

The Spanish Mac keyboard produced `¶`, not the shell pipe `|`.

**Fix**

Run `env | grep APP`. If needed, paste the pipe character or use a keyboard layout that exposes it predictably.

**Lesson**

Visually similar or unfamiliar keyboard symbols can change shell parsing completely.

## `$POD_NAME` empty in the logs terminal

**Symptom**

```text
error: You must provide one or more resources by argument or filename.
```

**Cause**

The variable had been set in another terminal. The current shell expanded `"$POD_NAME"` to an empty string.

**Fix**

Recreate and echo the variable in that terminal, or supply the exact Pod name.

**Lesson**

Validate generated shell variables before using them. A label query returning the first Pod also may not select the replica that handled a specific request.

## Logs followed on the other replica

**Symptom**

Requests succeeded, but expected HTTP access lines did not appear in the selected stream.

**Cause**

The Service had two endpoints and could route the connection to either Pod.

**Fix**

Use the `hostname` returned by this Flask application to identify the serving Pod, then follow that Pod's logs and generate another request.

**Lesson**

In a replicated service, correlate requests using instance identity and, preferably, a request/correlation ID.

## Flask production warning

**Symptom**

```text
WARNING: This is a development server. Do not use it in a production deployment.
```

**Cause**

The container runs Flask's built-in development server.

**Resolution for production**

Run the application behind a production WSGI server such as Gunicorn, configure graceful shutdown and probes, and expose it through the platform's normal ingress path.

