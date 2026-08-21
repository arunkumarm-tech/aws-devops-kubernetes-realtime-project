# 01 — Project and Jenkins Setup

## Starting point

Day 10 reused the Day 9 application, Dockerfile, Kubernetes manifests, and `eks/eks-cluster.yaml`. Remote Day 9 documentation was synchronized into the local working tree before pipeline work so the local branch and GitHub `main` represented the same history. The session discussed reviewing local state with `git status`, retrieving remote work with `git pull origin main`, and confirming the Day 8/9 documentation before adding Day 10 changes. No conflict or destructive reset was recorded.

The important workflow principle was:

```text
GitHub main is the shared source of truth
        ↓
local repository is synchronized
        ↓
Jenkins checks out the same main branch
```

## Jenkins job

The job was named `arun-devops-day10-cicd` and configured as a Pipeline using **Pipeline script from SCM**:

- SCM: Git
- Repository: `https://github.com/arunkumarm-tech/aws-devops-kubernetes-realtime-project.git`
- Branch: `main`
- Script path: `Jenkinsfile`

This kept the pipeline versioned beside the code and allowed each Jenkins run to report the exact commit it checked out. The repository was public for this lab, so the console reported `No credentials specified` for Git checkout.

## First useful failure

Build 2 proved that SCM configuration and pipeline parsing worked:

```text
Obtained Jenkinsfile from git ...
Checking out Revision 22764ca... (refs/remotes/origin/main)
Commit message: "Add Day 10 Jenkins pipeline"
```

It then failed in the Docker stage:

```text
+ docker build -f docker/Dockerfile -t arun-jenkins-flask-app:build-2 .
docker: command not found
ERROR: script returned exit code 127
Finished: FAILURE
```

This isolated the problem to the Jenkins service environment, not Git, SCM, or Declarative Pipeline syntax.

## Git workflow used throughout Day 10

Each pipeline evolution followed the same small-change cycle:

```bash
git diff Jenkinsfile
git add Jenkinsfile
git commit -m "<focused change>"
git push origin main
```

Recorded commit messages included:

- `Add Day 10 Jenkins pipeline`
- `Fix Jenkins Docker PATH`
- `Add AWS CLI check to Jenkins pipeline`
- `Add AWS identity check to Jenkins pipeline`
- `Add AWS credentials binding to Jenkins pipeline`
- `Add ECR login stage to Jenkins pipeline`
- `Add ECR image tag and push stages`
- `Add kubectl CLI check to Jenkins pipeline`
- `Add EKS access configuration to Jenkins pipeline`
- `Add automated EKS deployment stage`
- `Fix Jenkins Docker build for EKS amd64 nodes`
- `Add post-deployment verification stage`

Small commits made each failure attributable to one change and made rollback or review straightforward.
