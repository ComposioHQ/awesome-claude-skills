# CI: CircleCI, Azure DevOps, and Jenkins

> **When to use**: Running Playwright tests in CI platforms other than GitHub Actions or GitLab. Each section provides a production-ready config you can copy and adapt.

## Quick Reference

```bash
# Common across all CI platforms
npx playwright install --with-deps    # install browsers + OS deps
npx playwright test --shard=1/4       # shard for parallelism
npx playwright merge-reports ./blob-report  # merge shard results
npx playwright test --reporter=dot,html     # multiple reporters
```

## Patterns

### Pattern 1: CircleCI

**Use when**: Your project runs on CircleCI.

#### Basic Pipeline

```yaml
# .circleci/config.yml
version: 2.1

executors:
  playwright:
    docker:
      - image: mcr.microsoft.com/playwright:v1.52.0-noble
    working_directory: ~/project

jobs:
  install:
    executor: playwright
    steps:
      - checkout
      - restore_cache:
          keys:
            - npm-deps-{{ checksum "package-lock.json" }}
      - run: npm ci
      - save_cache:
          key: npm-deps-{{ checksum "package-lock.json" }}
          paths:
            - node_modules
      - persist_to_workspace:
          root: .
          paths:
            - node_modules

  test:
    executor: playwright
    parallelism: 4
    steps:
      - checkout
      - attach_workspace:
          at: .
      - run:
          name: Run Playwright tests
          command: |
            npx playwright test --shard=$((CIRCLE_NODE_INDEX + 1))/$CIRCLE_NODE_TOTAL
      - store_artifacts:
          path: playwright-report
          destination: playwright-report
      - store_artifacts:
          path: test-results
          destination: test-results
      - store_test_results:
          path: test-results/junit.xml

workflows:
  test:
    jobs:
      - install
      - test:
          requires:
            - install
```

**Config for CircleCI JUnit integration:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [
        ['dot'],
        ['html', { open: 'never' }],
        ['junit', { outputFile: 'test-results/junit.xml' }],
      ]
    : [['html', { open: 'on-failure' }]],
});
```

#### CircleCI with Orbs (Simplified)

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  node: circleci/node@6.1

executors:
  playwright:
    docker:
      - image: mcr.microsoft.com/playwright:v1.52.0-noble

jobs:
  e2e:
    executor: playwright
    parallelism: 4
    steps:
      - checkout
      - node/install-packages
      - run:
          name: Run tests
          command: npx playwright test --shard=$((CIRCLE_NODE_INDEX + 1))/$CIRCLE_NODE_TOTAL
      - store_artifacts:
          path: playwright-report
      - store_test_results:
          path: test-results/junit.xml

workflows:
  main:
    jobs:
      - e2e
```

---

### Pattern 2: Azure DevOps

**Use when**: Your project runs on Azure DevOps Pipelines.

#### Basic Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main

pr:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  CI: 'true'
  npm_config_cache: $(Pipeline.Workspace)/.npm

steps:
  - task: NodeTool@0
    inputs:
      versionSpec: '20.x'
    displayName: 'Install Node.js'

  - task: Cache@2
    inputs:
      key: 'npm | "$(Agent.OS)" | package-lock.json'
      restoreKeys: |
        npm | "$(Agent.OS)"
      path: $(npm_config_cache)
    displayName: 'Cache npm'

  - script: npm ci
    displayName: 'Install dependencies'

  - script: npx playwright install --with-deps
    displayName: 'Install Playwright browsers'

  - script: npx playwright test
    displayName: 'Run Playwright tests'

  - task: PublishTestResults@2
    condition: always()
    inputs:
      testResultsFormat: 'JUnit'
      testResultsFiles: 'test-results/junit.xml'
      mergeTestResults: true
      testRunTitle: 'Playwright Tests'
    displayName: 'Publish test results'

  - task: PublishPipelineArtifact@1
    condition: always()
    inputs:
      targetPath: playwright-report
      artifact: playwright-report
      publishLocation: 'pipeline'
    displayName: 'Upload report'
```

**Config for Azure DevOps JUnit integration:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [
        ['dot'],
        ['html', { open: 'never' }],
        ['junit', { outputFile: 'test-results/junit.xml' }],
      ]
    : [['html', { open: 'on-failure' }]],
});
```

#### Azure DevOps with Sharding

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main

pr:
  branches:
    include:
      - main

variables:
  CI: 'true'

stages:
  - stage: Test
    jobs:
      - job: Playwright
        pool:
          vmImage: 'ubuntu-latest'
        strategy:
          matrix:
            shard1:
              SHARD: '1/4'
            shard2:
              SHARD: '2/4'
            shard3:
              SHARD: '3/4'
            shard4:
              SHARD: '4/4'
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '20.x'

          - script: npm ci
            displayName: 'Install dependencies'

          - script: npx playwright install --with-deps
            displayName: 'Install browsers'

          - script: npx playwright test --shard=$(SHARD)
            displayName: 'Run tests (shard $(SHARD))'

          - task: PublishPipelineArtifact@1
            condition: always()
            inputs:
              targetPath: blob-report
              artifact: blob-report-$(System.JobPositionInPhase)
            displayName: 'Upload blob report'

  - stage: Report
    dependsOn: Test
    condition: always()
    jobs:
      - job: MergeReports
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '20.x'

          - script: npm ci
            displayName: 'Install dependencies'

          - task: DownloadPipelineArtifact@2
            inputs:
              patterns: 'blob-report-*/**'
              path: all-blob-reports
            displayName: 'Download all blob reports'

          - script: npx playwright merge-reports --reporter=html ./all-blob-reports
            displayName: 'Merge reports'

          - task: PublishPipelineArtifact@1
            inputs:
              targetPath: playwright-report
              artifact: playwright-report
            displayName: 'Upload merged report'
```

---

### Pattern 3: Jenkins

**Use when**: Your project runs on Jenkins.

#### Jenkinsfile (Declarative Pipeline)

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.52.0-noble'
            args '-u root'  // Playwright needs root in container
        }
    }

    environment {
        CI = 'true'
        HOME = '/root'
        npm_config_cache = "${WORKSPACE}/.npm"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }

        stage('Test') {
            steps {
                sh 'npx playwright test'
            }
            post {
                always {
                    // Publish JUnit results
                    junit allowEmptyResults: true,
                         testResults: 'test-results/junit.xml'

                    // Archive HTML report
                    archiveArtifacts artifacts: 'playwright-report/**',
                                     allowEmptyArchive: true

                    // Archive traces on failure
                    archiveArtifacts artifacts: 'test-results/**',
                                     allowEmptyArchive: true
                }
            }
        }
    }

    post {
        failure {
            // Notify on failure (Slack, email, etc.)
            echo 'Playwright tests failed!'
        }
        cleanup {
            cleanWs()
        }
    }
}
```

**Config for Jenkins JUnit integration:**

```ts
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: process.env.CI
    ? [
        ['dot'],
        ['html', { open: 'never' }],
        ['junit', { outputFile: 'test-results/junit.xml' }],
      ]
    : [['html', { open: 'on-failure' }]],
});
```

#### Jenkins with Parallel Stages

```groovy
// Jenkinsfile (sharded)
pipeline {
    agent none

    environment {
        CI = 'true'
        HOME = '/root'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Test') {
            parallel {
                stage('Shard 1') {
                    agent {
                        docker {
                            image 'mcr.microsoft.com/playwright:v1.52.0-noble'
                            args '-u root'
                        }
                    }
                    steps {
                        sh 'npm ci'
                        sh 'npx playwright test --shard=1/4'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'blob-report/**',
                                             allowEmptyArchive: true
                        }
                    }
                }
                stage('Shard 2') {
                    agent {
                        docker {
                            image 'mcr.microsoft.com/playwright:v1.52.0-noble'
                            args '-u root'
                        }
                    }
                    steps {
                        sh 'npm ci'
                        sh 'npx playwright test --shard=2/4'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'blob-report/**',
                                             allowEmptyArchive: true
                        }
                    }
                }
                stage('Shard 3') {
                    agent {
                        docker {
                            image 'mcr.microsoft.com/playwright:v1.52.0-noble'
                            args '-u root'
                        }
                    }
                    steps {
                        sh 'npm ci'
                        sh 'npx playwright test --shard=3/4'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'blob-report/**',
                                             allowEmptyArchive: true
                        }
                    }
                }
                stage('Shard 4') {
                    agent {
                        docker {
                            image 'mcr.microsoft.com/playwright:v1.52.0-noble'
                            args '-u root'
                        }
                    }
                    steps {
                        sh 'npm ci'
                        sh 'npx playwright test --shard=4/4'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'blob-report/**',
                                             allowEmptyArchive: true
                        }
                    }
                }
            }
        }
    }
}
```

## Decision Guide

| CI Platform | Docker Image Support | Native Parallelism | Artifact Browsing | JUnit Integration |
|---|---|---|---|---|
| CircleCI | First-class (`docker:` executor) | `parallelism: N` with `CIRCLE_NODE_INDEX` | Via artifacts tab | `store_test_results` |
| Azure DevOps | Via `vmImage` or container jobs | `strategy.matrix` | Pipeline Artifacts UI | `PublishTestResults@2` |
| Jenkins | Docker Pipeline plugin | `parallel` stages | Archived Artifacts | `junit` step |

| Scenario | CircleCI | Azure DevOps | Jenkins |
|---|---|---|---|
| Shard variable | `$((CIRCLE_NODE_INDEX + 1))/$CIRCLE_NODE_TOTAL` | Define in matrix: `SHARD: '1/4'` | Hardcode per parallel stage |
| Cache key | `checksum "package-lock.json"` | `Cache@2` with key template | `stash`/`unstash` or shared volume |
| Secrets | Context + environment variables | Variable groups + pipeline variables | Credentials plugin |
| Report upload | `store_artifacts` | `PublishPipelineArtifact@1` | `archiveArtifacts` |

## Anti-Patterns

| Anti-Pattern | Problem | Do This Instead |
|---|---|---|
| Installing browsers on bare metal without `--with-deps` | Missing OS libs cause launch failures | Use Playwright Docker image or `--with-deps` flag |
| No JUnit reporter | CI platform can't display test results natively | Add `['junit', { outputFile: 'test-results/junit.xml' }]` |
| Unlimited job timeout | Hung tests run indefinitely, consuming CI resources | Set explicit timeout (20-30 min) |
| No artifact upload on success | Can't verify results when tests pass | Always upload reports (`condition: always()` / `when: always`) |
| Running browsers as non-root in container without setup | Permission errors on browser binaries | Run as root or configure proper permissions |
| Hardcoding shard count in config instead of using CI variables | Must update two places when changing parallelism | Use CI-native variables (`CI_NODE_TOTAL`, `CIRCLE_NODE_TOTAL`) |

## Troubleshooting

### CircleCI: "Error: browserType.launch: Executable doesn't exist"

**Cause**: Not using the Playwright Docker image, or image version doesn't match `@playwright/test` version.

**Fix**: Match image tag to your Playwright version:

```yaml
docker:
  - image: mcr.microsoft.com/playwright:v1.52.0-noble  # match package.json version
```

### Azure DevOps: Test results not showing in Tests tab

**Cause**: JUnit reporter not configured, or `PublishTestResults@2` task missing.

**Fix**: Add both the reporter and the publish task:

```ts
// playwright.config.ts
reporter: [['junit', { outputFile: 'test-results/junit.xml' }]],
```

```yaml
- task: PublishTestResults@2
  condition: always()
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: 'test-results/junit.xml'
```

### Jenkins: "Browser closed unexpectedly" in Docker agent

**Cause**: Running as non-root user in container. Chromium's sandbox needs root or `--no-sandbox`.

**Fix**: Run as root in the Docker agent:

```groovy
agent {
    docker {
        image 'mcr.microsoft.com/playwright:v1.52.0-noble'
        args '-u root'
    }
}
environment {
    HOME = '/root'
}
```

### All platforms: Shard index off by one

**Cause**: CircleCI's `CIRCLE_NODE_INDEX` is 0-based, but Playwright's `--shard` is 1-based.

**Fix**: Add 1 to the index for CircleCI:

```yaml
# CircleCI
command: npx playwright test --shard=$((CIRCLE_NODE_INDEX + 1))/$CIRCLE_NODE_TOTAL

# GitLab (already 1-based)
command: npx playwright test --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
```

## Related

- [ci/ci-github-actions.md](ci-github-actions.md) -- GitHub Actions configuration
- [ci/ci-gitlab.md](ci-gitlab.md) -- GitLab CI configuration
- [ci/parallel-and-sharding.md](parallel-and-sharding.md) -- sharding strategies
- [ci/docker-and-containers.md](docker-and-containers.md) -- Docker image details
- [ci/reporting-and-artifacts.md](reporting-and-artifacts.md) -- reporter configuration for CI
