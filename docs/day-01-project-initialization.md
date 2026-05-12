# Day 1 - Project Initialization

## Objective
Set up a professional GitHub repository structure for an end-to-end AWS DevOps and Kubernetes real-time project.

---

## Activities Completed
1. Created a public GitHub repository:
   aws-devops-kubernetes-realtime-project

2. Cloned the repository to the local MacBook.

3. Created the following folder structure:
   - application/
   - docker/
   - jenkins/
   - kubernetes/
   - terraform/
   - monitoring/
   - scripts/
   - docs/

4. Added `.gitkeep` files to ensure empty folders are tracked by Git.

5. Created initial files:
   - README.md
   - .gitignore
   - docs/day-01-project-initialization.md

6. Committed and pushed the changes to GitHub.

---

## Commands Used

```bash
mkdir -p ~/Projects
cd ~/Projects

git clone https://github.com/arunkumarm-tech/aws-devops-kubernetes-realtime-project.git
cd aws-devops-kubernetes-realtime-project

mkdir -p application docker jenkins kubernetes terraform monitoring scripts docs

touch application/.gitkeep docker/.gitkeep jenkins/.gitkeep \
      kubernetes/.gitkeep terraform/.gitkeep monitoring/.gitkeep \
      scripts/.gitkeep

touch docs/day-01-project-initialization.md

git add .
git commit -m "Day 1: Initialize project structure"
git push origin main
