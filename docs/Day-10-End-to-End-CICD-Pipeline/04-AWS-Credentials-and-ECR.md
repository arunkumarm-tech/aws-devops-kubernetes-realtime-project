# 04 — AWS Credentials and Amazon ECR

## AWS CLI discovery

The local identity and binary location were checked first:

```bash
aws sts get-caller-identity
which aws
```

Actual identity:

```json
{
  "Account": "160827082645",
  "Arn": "arn:aws:iam::160827082645:user/arun-devops"
}
```

The AWS CLI was at `/opt/homebrew/bin/aws`, so Jenkins' PATH became:

```groovy
PATH = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
```

The `AWS CLI Check` stage returned `aws-cli/2.33.19 ... source/arm64` and finished successfully.

## AWS Credentials plugin

Jenkins initially offered no `AWS Credentials` kind. The recorded resolution was:

1. Open **Manage Jenkins → Plugins → Available plugins**.
2. Install **AWS Credentials**.
3. Restart Jenkins.
4. Open **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**.
5. Select **AWS Credentials**.
6. Store the IAM access key pair with ID `aws-devops-credentials`.

Because Jenkins ran on the Mac, the AWS access-key use case selected was **Application running outside AWS**. Secret material was entered only in Jenkins and never added to Git.

Credential binding was verified with:

```groovy
withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                  credentialsId: 'aws-devops-credentials']]) {
    sh 'aws sts get-caller-identity'
}
```

Jenkins reported that it masked `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY`, then returned the expected IAM identity.

## ECR authentication, tagging, and push

```bash
aws ecr get-login-password --region us-east-1 \
| docker login \
  --username AWS \
  --password-stdin 160827082645.dkr.ecr.us-east-1.amazonaws.com
```

Expected and actual result: `Login Succeeded`.

```bash
docker tag \
  arun-jenkins-flask-app:build-8 \
  160827082645.dkr.ecr.us-east-1.amazonaws.com/arun-jenkins-flask-app:build-8

docker push \
  160827082645.dkr.ecr.us-east-1.amazonaws.com/arun-jenkins-flask-app:build-8
```

Build 8 completed with digest:

```text
sha256:617dde81de93a6d301c40c39d6a622c5f35d46af0849ddfe25f47c8eb64bf1f8
```

The first verification query failed because table output encountered a row with only one projected element:

```bash
aws ecr describe-images \
  --repository-name arun-jenkins-flask-app \
  --region us-east-1 \
  --query 'imageDetails[*].[imageTags,imageDigest]' \
  --output table
```

Actual error:

```text
Row should have 2 elements, instead it has 1
```

The query was narrowed to the known tag:

```bash
aws ecr describe-images \
  --repository-name arun-jenkins-flask-app \
  --image-ids imageTag=build-8 \
  --region us-east-1 \
  --query 'imageDetails[0].{Tag:imageTags[0],Digest:imageDigest,PushedAt:imagePushedAt,SizeBytes:imageSizeInBytes}' \
  --output table
```

ECR returned the same digest, tag `build-8`, and image size `48,438,144` bytes. That digest match proved the registry contained the artifact Jenkins pushed.
