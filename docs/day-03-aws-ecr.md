cd ~/Projects/aws-devops-kubernetes-realtime-project

python3 <<'PY'
from pathlib import Path

content = r"""# Day 4 - Jenkins Installation and CI Pipeline

## 1. Objective

The objective of Day 4 is to install Jenkins, configure it locally, create the first Jenkins job, integrate Jenkins with GitHub, troubleshoot build failures, and complete the first successful CI build.

---

## 2. Architecture Overview

```text
GitHub Repository
        |
        v
Jenkins Freestyle Job
        |
        v
Jenkins Workspace
        |
        v
Shell Build Steps
        |
        v
Console Output / Build Result


3. Prerequisites

Before starting Day 4, the following were required:

* macOS terminal access
* Homebrew installed
* GitHub repository already created
* Docker project files already available
* Java 17 required for Jenkins
* Jenkins installed using Homebrew

⸻

4. Step-by-Step Tasks Performed

Step 1: Checked Java Version

java -version

nitial output:
The operation couldn’t be completed. Unable to locate a Java Runtime.

This confirmed Java was either not installed correctly or not configured in the terminal path.

⸻

Step 2: Verified Homebrew
brew --version
Output
Homebrew 5.1.14

Step 3: Configured Java 17

The first Java path configuration did not work, so we created the proper symlink and updated shell configuration.

sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk

echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

java -version
echo $JAVA_HOME

Successful output:

openjdk version "17.0.19"
JAVA_HOME=/opt/homebrew/Cellar/openjdk@17/17.0.19/libexec/openjdk.jdk/Contents/Home

Step 4: Installed Jenkins LTS
brew install jenkins-lts

Step 5: Started Jenkins Service
brew services start jenkins-lts

Step 6: Verified Jenkins Service
brew services list | grep jenkins

Output:
jenkins-lts started arunkumarm ~/Library/LaunchAgents/homebrew.mxcl.jenkins-lts.plist

Step 7: Opened Jenkins in Browser
open http://localhost:8080


Jenkins opened at:
http://localhost:8080

Step 8: Unlocked Jenkins

Jenkins generated the initial administrator password at:

/Users/arunkumarm/.jenkins/secrets/initialAdminPassword

This file is used only during first-time Jenkins setup.

⸻

Step 9: Installed Suggested Plugins

In Jenkins setup wizard, selected:

Install suggested plugins

This installed common plugins such as:

* Git plugin
* Pipeline plugins
* Credentials plugin
* Build tools support
* UI and Jenkins core plugins

⸻

Step 10: Created Admin User

Created Jenkins admin user during the setup wizard.

⸻

Step 11: Configured Jenkins URL

Configured Jenkins URL as:

http://localhost:8080/

Step 12: Created First Freestyle Job

Created Jenkins job:

arun-flask-build

Job type:

Freestyle Project

Step 13: Added First Shell Build Step

Initial shell commands:

echo "Hello Arun"
pwd
whoami
date

Build #1 completed successfully.

⸻

Step 14: Integrated Jenkins with GitHub

Configured Source Code Management as Git.

Repository URL:

https://github.com/arunkumarm-tech/aws-devops-kubernetes-realtime-project.git

No credentials were required because the repository is public.

⸻

Step 15: Build #2 Failed

Build #2 failed with the error:

ERROR: Couldn't find any revision to build. Verify the repository and branch configuration for this job.

Root cause:
Jenkins was configured to build */master, but the GitHub repository branch is main.

Step 16: Fixed Branch Configuration

Changed branch configuration from:

*/master

to:

*/main

Step 17: Updated Build Commands

Updated Jenkins shell build commands:

echo "Jenkins Build Started"

pwd

ls -la

echo "Repository Files"

find . -type f | head -30

echo "Build Completed"

Step 18: Build #3 Completed Successfully

Build output confirmed:

Finished: SUCCESS

Jenkins successfully checked out the repository and executed build steps.

⸻

5. Commands Used

java -version

brew --version

sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk

echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

java -version
echo $JAVA_HOME

brew install jenkins-lts

brew services start jenkins-lts

brew services list | grep jenkins

open http://localhost:8080

Jenkins build shell commands:

echo "Jenkins Build Started"

pwd

ls -la

echo "Repository Files"

find . -type f | head -30

echo "Build Completed"

6. Configuration Files

No new project configuration file was created on Day 4.

Jenkins internal configuration files are stored inside:

/Users/arunkumarm/.jenkins

Important Jenkins directories:

/Users/arunkumarm/.jenkins/jobs
/Users/arunkumarm/.jenkins/workspace
/Users/arunkumarm/.jenkins/plugins
/Users/arunkumarm/.jenkins/secrets
/Users/arunkumarm/.jenkins/users

Initial admin password location:

/Users/arunkumarm/.jenkins/secrets/initialAdminPassword

Workspace used by our job:
/Users/arunkumarm/.jenkins/workspace/arun-flask-build

7. Detailed Explanation

What is Jenkins?

Jenkins is an open-source automation server used to implement CI/CD pipelines. It automates build, test, package, and deployment activities.

⸻

Why Jenkins Requires Java

Jenkins is a Java-based application. Java must be installed and configured before Jenkins can start.

⸻

What is Jenkins Home?

Jenkins Home is the main directory where Jenkins stores its configuration, jobs, plugins, users, workspaces, secrets, and build history.

On this MacBook:

/Users/arunkumarm/.jenkins

What is a Jenkins Job?

A Jenkins job is a unit of work that Jenkins executes. It can run shell commands, build code, run tests, build Docker images, or deploy applications.

⸻

What is a Freestyle Project?

A freestyle project is the simplest Jenkins job type. It allows users to configure build steps using the Jenkins UI without writing a Jenkinsfile.

⸻

What is Jenkins Workspace?

A workspace is the directory where Jenkins checks out source code and executes build commands.

Our workspace:

/Users/arunkumarm/.jenkins/workspace/arun-flask-build

What is Console Output?

Console Output shows the logs generated during a Jenkins build. It is used to troubleshoot build failures and verify build execution.

⸻

What is CI?

CI stands for Continuous Integration. It means developers frequently push code to a shared repository, and Jenkins automatically pulls, builds, and validates the code.

⸻

8. Troubleshooting Scenarios

Scenario 1: Java Runtime Not Found

Error:

Unable to locate a Java Runtime.

Root cause:

Java 17 was installed but not properly linked and configured in the shell.

Fix:

sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk

echo 'export JAVA_HOME=$(/usr/libexec/java_home -v 17)' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

Scenario 2: Jenkins Build Failed Due to Branch Mismatch

Error:

ERROR: Couldn't find any revision to build. Verify the repository and branch configuration for this job.

Root cause:

Jenkins was configured to build:

*/master

but the GitHub repository branch was:

main

Fix:

Changed branch specifier to:

*/main

Scenario 3: Jenkins Initial Admin Password

Question:

What is /Users/arunkumarm/.jenkins/secrets/initialAdminPassword?

Answer:

It is the temporary password generated by Jenkins during the first startup to unlock Jenkins securely.

⸻

Scenario 4: Git Tool Warning

Observed:

The recommended git tool is: NONE

Explanation:

Jenkins detected system Git and used it successfully. This warning is not a build blocker in this setup.

⸻

9. Real-Time Use Cases

In real projects, Jenkins is used to:

* Pull source code from GitHub
* Build applications
* Run automated tests
* Build Docker images
* Push images to ECR
* Deploy applications to Kubernetes or EKS
* Trigger pipelines automatically after code changes

Real-time flow:

Developer pushes code
        |
        v
GitHub repository
        |
        v
Jenkins job
        |
        v
Code checkout
        |
        v
Build and validation
        |
        v
Docker / ECR / Kubernetes deployment


10. Interview Explanation

I installed Jenkins locally on macOS using Homebrew. Since Jenkins requires Java, I installed and configured OpenJDK 17 by setting JAVA_HOME and updating PATH. After starting Jenkins as a service, I completed the initial setup, installed suggested plugins, created an admin user, and configured Jenkins URL.

Then I created a freestyle Jenkins job named arun-flask-build, executed a basic shell build, and integrated it with my GitHub repository. During GitHub integration, the build failed because Jenkins was looking for the master branch while my repository was using main. I analyzed the console output, identified the branch mismatch, changed the branch specifier to */main, and reran the build successfully.

This completed the basic Continuous Integration flow from GitHub to Jenkins workspace.

⸻

11. Interview Questions and Answers

Q1: What is Jenkins?

Jenkins is an open-source automation server used to implement CI/CD pipelines.

⸻

Q2: Why does Jenkins require Java?

Jenkins is a Java-based application, so it requires Java Runtime Environment or JDK to run.

⸻

Q3: Which Java version did you use for Jenkins?

I used OpenJDK 17.

⸻

Q4: What is JAVA_HOME?

JAVA_HOME is an environment variable that points to the installed Java directory.

⸻

Q5: What is PATH?

PATH is an environment variable that tells the shell where to find executable commands.

⸻

Q6: How did you install Jenkins on macOS?

Using Homebrew:

brew install jenkins-lts
brew services start jenkins-lts

Q7: How do you verify Jenkins service status on macOS?
brew services list | grep jenkins

Q8: What is Jenkins Home?

Jenkins Home is the directory where Jenkins stores jobs, plugins, users, workspaces, secrets, and configuration.

⸻

Q9: Where is Jenkins Home on your Mac?

/Users/arunkumarm/.jenkins

Q10: What is initialAdminPassword?

It is the temporary password generated by Jenkins during first-time setup to unlock Jenkins.

⸻

Q11: What is a Jenkins job?

A Jenkins job is a configured task that Jenkins executes, such as build, test, or deploy.

⸻

Q12: What is a freestyle project?

A freestyle project is a basic Jenkins job type configured through the Jenkins UI.

⸻

Q13: What is Jenkins workspace?

Workspace is the directory where Jenkins checks out code and runs build commands.

⸻

Q14: What was your Jenkins workspace path?

/Users/arunkumarm/.jenkins/workspace/arun-flask-build

Q15: What is Console Output?

Console Output shows build execution logs and helps troubleshoot build failures.

⸻

Q16: How did Jenkins connect to GitHub?

Using Git Source Code Management with the repository URL:

https://github.com/arunkumarm-tech/aws-devops-kubernetes-realtime-project.git

Q17: Why did Build #2 fail?

Because Jenkins was trying to build the master branch, but the repository branch was main.

⸻

Q18: How did you fix the Jenkins branch issue?

I changed the branch specifier from:

*/master

to

*/main

Q19: What is Continuous Integration?

Continuous Integration is the practice of frequently merging code changes into a shared repository and automatically building/testing them.

⸻

Q20: What is the difference between GitHub and Jenkins?

GitHub stores and versions source code. Jenkins automates build, test, and deployment processes.

⸻

Q21: What is a Jenkins plugin?

A plugin extends Jenkins functionality, such as Git integration, pipelines, credentials, and Docker support.

⸻

Q22: What plugins were installed initially?

Suggested plugins, including Git, Pipeline, Credentials, and common build-related plugins.

⸻

Q23: How do you troubleshoot Jenkins build failures?

Check Console Output, verify repository URL, branch name, credentials, plugin availability, workspace, and build commands.

⸻

Q24: What does “Running as SYSTEM” mean?

It means the build was executed by Jenkins internal system user.

⸻

Q25: What is the importance of Jenkins in DevOps?

Jenkins automates CI/CD workflows and reduces manual deployment effort.

⸻

12. Key Learnings

* Jenkins requires Java.
* Java installation alone is not enough; JAVA_HOME and PATH must be configured.
* Jenkins can run as a local service using Homebrew.
* Jenkins stores configuration inside Jenkins Home.
* Freestyle jobs are useful for basic CI tasks.
* Console Output is the first place to check for build failures.
* Jenkins workspace stores checked-out repository code.
* Branch mismatch is a common Jenkins GitHub integration issue.
* Jenkins can pull code from GitHub and execute shell commands.

⸻

13. Resume Points

* Installed and configured Jenkins LTS on macOS using Homebrew.
* Configured Java 17, JAVA_HOME, and PATH for Jenkins execution.
* Created Jenkins freestyle job for CI automation.
* Integrated Jenkins with GitHub repository.
* Troubleshot Jenkins Git branch mismatch issue.
* Verified Jenkins workspace and source code checkout.
* Executed successful Jenkins CI build from GitHub source code.

⸻

14. Git Commands Used

cd ~/Projects/aws-devops-kubernetes-realtime-project

git add docs/day-04-jenkins.md

git commit -m "Day 4: Add Jenkins installation and CI pipeline documentation"

git push origin main

git status

