# 03 — Docker Build and Local Validation

Before automating delivery, the application image was built and the application and `/health` endpoint were validated locally. The Dockerfile used `python:3.12-slim`, installed `application/requirements.txt`, copied `application/app.py`, and served the Flask app on port 5000.

Representative commands used in the local validation flow were:

```bash
docker build -f docker/Dockerfile -t arun-jenkins-flask-app:day10-local .
docker run --rm -d --name arun-day10-local -p 5000:5000 arun-jenkins-flask-app:day10-local
curl http://localhost:5000
curl http://localhost:5000/health
docker stop arun-day10-local
```

The important acceptance criteria were a project JSON response on `/` and:

```json
{"status":"healthy"}
```

## Jenkins build 2: PATH failure

Jenkins reached the Docker stage but returned exit code 127:

```text
docker: command not found
```

The interactive terminal located Docker with:

```bash
which docker
```

Actual result:

```text
/usr/local/bin/docker
```

The fix was committed as `Fix Jenkins Docker PATH`:

```groovy
PATH = "/usr/local/bin:${env.PATH}"
```

## Jenkins build 3: first successful image

After the PATH correction Jenkins produced:

```text
docker build -f docker/Dockerfile -t arun-jenkins-flask-app:build-3 .
Finished: SUCCESS
```

The image was verified outside Jenkins:

```bash
docker images | grep build-3
```

Actual output included:

```text
arun-jenkins-flask-app:build-3 ... 223MB 48.4MB
```

Internally, Docker reused cached layers for `WORKDIR`, dependency installation, and application copy where inputs had not changed. The Jenkins build number became part of the image tag, linking the artifact to its pipeline execution.

## Cross-platform correction

The original `docker build` on the Apple Silicon Jenkins host produced an ARM64-compatible image. EKS `t3.small` nodes reported an `x86_64` kernel. The corrected build was:

```bash
docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t ${IMAGE_NAME}:${IMAGE_TAG} \
  --load \
  .
```

`--platform linux/amd64` selected the worker architecture. `--load` imported the result into the local Docker image store so the later `docker tag` and `docker push` stages could use it.
