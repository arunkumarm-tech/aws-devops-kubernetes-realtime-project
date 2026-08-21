# Mistakes We Made

These are useful engineering lessons, not items to hide.

## Started a second cluster creation

The first `eksctl create cluster` was still provisioning when another create was started. CloudFormation correctly rejected the duplicate stack name. The lesson is to check stack status from a second terminal instead of rerunning creation.

## Assumed cluster creation was fully complete

The control plane completed, but the node group and core add-ons had not. A cluster name alone does not prove a usable Kubernetes platform. Verify node groups, node readiness, and `kube-system`.

## Built for the host architecture

Plain `docker build` on Apple Silicon produced an image unsuitable for AMD64 `t3.small` workers. Target architecture is part of the artifact contract.

## Treated a rollout timeout as the failure

The timeout was only the observable symptom. Pod status and Events revealed the platform mismatch. Always continue from controller status to pod-level evidence.

## Used a Jenkins-only environment command locally

`WORKSPACE` was not a normal terminal variable. Exporting `${WORKSPACE}/.kubeconfig` locally risked pointing kubectl at an unintended path. `unset KUBECONFIG` restored the normal behavior.

## Added stages with misplaced braces

Manual Jenkinsfile edits temporarily nested stages or placed them outside `stages`. Repeated `cat`, `tail`, `sed`, and `git diff` checks caught these before commits. A linter or IDE would reduce this class of error.

## Used a brittle ECR table query

The first JMESPath assumed all rows had tags. Narrowing to `imageTag=build-8` avoided irregular rows and matched the actual verification goal.

## Expected `set image` to work on a fresh cluster

The Deployment did not yet exist. A delivery pipeline must either apply the complete desired state or clearly define bootstrap prerequisites.

## Opened NodePort to the world

`0.0.0.0/0` was acceptable only for the short-lived learning test. It increases exposure and is not a production ingress design.

## Relied on a weak local Jenkins password

The lab used a weak credential. Even local services should use a strong password, and Jenkins must never be exposed externally with lab credentials.
