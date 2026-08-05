# `kubectl exec`

## Objective

Run commands in the live Flask container to inspect its working directory, files, and injected environment.

## Successful session

```bash
echo "$POD_NAME"

kubectl exec -it "$POD_NAME" \
  -n arun-devops -- sh
```

Inside the container:

```text
# pwd
/app

# ls -la
app.py
requirements.txt

# env | grep APP
APP_MESSAGE=Running from Kubernetes ConfigMap
APP_ENV=development

# env | grep DB
DB_USERNAME=admin
DB_PASSWORD=<redacted>

# exit
```

The changed prompt and `/app` path confirmed that the commands were running in the container rather than on the Mac. `-i` kept standard input open, `-t` allocated a terminal, and `--` separated kubectl arguments from the command executed in the container.

## Placeholder mistake

Before the successful session, this example was copied literally:

```bash
kubectl exec -it <pod-name> -- sh
```

zsh interpreted `<pod-name>` as shell redirection syntax and returned:

```text
zsh: no such file or directory: pod-name
```

The following `env`, resolver, `ping`, and `nslookup` commands therefore ran on macOS. Clues included `HOME=/Users/arunkumarm`, a project directory under `/Users`, and a `# macOS Notice` in `/etc/resolv.conf`. No Kubernetes container had been entered.

The correct approach is to replace placeholders with a real value or use a populated variable:

```bash
kubectl exec -it "$POD_NAME" -n arun-devops -- sh
```

## Keyboard issue

Inside the container, `env ¶ grep app` failed because `¶` is not the shell pipe. On the Spanish Mac keyboard the intended `|` character was difficult to locate. The corrected command was:

```bash
env | grep APP
```

Environment-variable names are case-sensitive, so `APP`/`APP_` was used rather than lowercase `app`.

## Production use and caution

`kubectl exec` is useful for narrow, time-bounded diagnosis: checking runtime configuration, DNS, filesystem contents, certificates, or connectivity from the same network namespace as the application. It should not be a way to patch a container manually. Changes inside a Pod are unreviewed and disappear when the Pod is replaced.

Minimal or distroless images may not include `sh`, `ping`, `nslookup`, or package managers. In that case, use application telemetry, an approved ephemeral debug container, or a dedicated diagnostic Pod. Access to `pods/exec` is powerful and should be restricted and audited through RBAC.

