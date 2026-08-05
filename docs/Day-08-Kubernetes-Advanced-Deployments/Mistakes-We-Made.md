# Mistakes We Made—and What They Taught Us

This is the most reusable part of Day 8. Each mistake exposed an assumption that would also matter during a real incident.

## We tagged the same image as `v2`

The rollout worked, but `v1` and `v2` shared image ID `b078bb59d51d`. We demonstrated the controller behavior without demonstrating a changed release. Next time, build a genuinely changed artifact and verify its digest.

## We expected three replicas to remain

The live Deployment had been scaled to three on Day 7, while the YAML still said two. Applying that YAML on Day 8 returned the Deployment to two. Kubernetes was not behaving unpredictably; two conflicting sources of intent had been used.

## We placed `env` at the wrong YAML level

The indentation looked plausible, but `env` was outside the container entry. The API rejected the Deployment patch. Reading the object hierarchy and validating before apply is more reliable than adjusting spaces by trial and error.

## We omitted the Secret namespace

The first `inventory-db-secret` went to the default namespace. Creating it again with `-n arun-devops` created a different Secret. Namespaces are part of a resource's identity and should be explicit in operational commands.

## We typed a placeholder literally

`kubectl exec -it <pod-name> -- sh` failed in zsh, but the next commands were still entered. They ran on the Mac, not in Kubernetes. The local `HOME`, project `PWD`, and macOS resolver notice were the evidence.

## We confused `¶` with `|`

The Spanish keyboard produced a paragraph symbol instead of a pipe. The shell treated it as an argument, so `env` reported a file error. The fixed command was `env | grep APP`.

## We reused a shell variable in another terminal

`$POD_NAME` was empty in the terminal used for live logs. Shell variables do not automatically cross terminal sessions. Echoing the variable before use would have made the problem obvious.

## We initially watched the wrong Pod's logs

The Service could send traffic to either of two endpoints. The application's response included a hostname, which identified the serving replica and allowed the logs to be correlated.

## We displayed a password while proving injection

`env | grep DB` provided clear learning evidence but also printed the password. The value is redacted in these pages and should be rotated if it protects anything real. In production, validate references and application connectivity without exposing plaintext.

## We treated “saved” and “applied” as the same thing

Saving a YAML file changes only the local file. `kubectl apply -f ...` submits its desired state to the cluster. `kubectl rollout status` then verifies reconciliation. Keeping those stages distinct helps locate failures:

```text
edit -> save -> validate/diff -> apply -> rollout -> application verification
```

## Final lesson

None of these were random failures. They fell into a small set of operational categories: source-of-truth drift, object hierarchy, namespace context, shell context, request correlation, and sensitive-data handling. Naming the category makes the next incident faster to diagnose.

