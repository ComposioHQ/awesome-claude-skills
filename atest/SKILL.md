# API Testing Skill (atest)

> **Claude Code Skill for api-testing (atest)**
> This skill helps you create, manage, and debug API test suites using the [api-testing](https://github.com/LinuxSuRen/api-testing) tool.

## How to Use This Skill

1. Copy this skill file to your Claude skills directory:
   ```bash
   # On macOS/Linux
   cp claude-skill.md ~/.claude/skills/api-testing.md

   # On Windows
   copy claude-skill.md %USERPROFILE%\.claude\skills\api-testing.md
   ```

2. Restart Claude Code to load the skill

3. Use trigger phrases like:
   - "create an API test suite"
   - "write a test for API"
   - "create grpc test"
   - "API load testing"
   - "mock API server"

## What is api-testing (atest)?

[api-testing](https://github.com/LinuxSuRen/api-testing) is a comprehensive API testing framework that supports:

- **Multi-protocol**: HTTP/REST, gRPC, GraphQL
- **Load Testing**: Duration-based, thread-based, QPS-based
- **Mock Server**: Create mock APIs from test suites
- **Code Generation**: Generate test code in Go, Python, Java, JavaScript
- **Multiple Reports**: Markdown, HTML, PDF, JSON, Prometheus
- **Web UI**: Built-in interface for test management

## Description

You are an expert in the api-testing tool (CLI command: `atest`), a comprehensive API testing framework written in Go. Help users create test suites in YAML format, run tests via CLI, debug failures, and utilize advanced features like load testing, mocking, and multi-protocol support (HTTP, gRPC, GraphQL).

## Trigger Phrases

- "create an API test suite"
- "write a test for API"
- "api-testing test" or "atest test"
- "create grpc test"
- "API load testing"
- "mock API server"
- "convert API tests"
- "debug test suite"

## Core Concepts

### Test Suite Structure

All test suites use YAML format with these key components:

```yaml
#!api-testing
name: TestSuiteName
api: https://api.example.com
param:
  key: value
items:
  - name: testCaseName
    request:
      api: /endpoint
      method: GET
      header:
        Authorization: Bearer {{.token}}
      body: |
        {"key": "value"}
    expect:
      statusCode: 200
      verify:
        - data.field == "expected"
    before:
      items:
        - "setupCommand()"
    after:
      items:
        - "teardownCommand()"
```

### Protocol Types

- **HTTP/REST** (default): Standard REST APIs
- **gRPC**: gRPC services with proto files
- **GraphQL**: GraphQL endpoints

### Key Features

1. **Templating**: Uses Sprig template functions with custom additions
2. **Data Sharing**: Response data from one test available in subsequent tests via `data.field`
3. **Verification**: Expression-based verification using `expr` library
4. **Load Testing**: Duration-based, thread-based, or QPS-based
5. **Mock Server**: Create mock APIs from test suites
6. **Report Formats**: Markdown, HTML, PDF, JSON, Prometheus

## Common Commands

```bash
# Run a test suite
atest run -p testsuite.yaml

# Run with load testing
atest run -p testsuite.yaml --duration 1m --thread 3 --qps 10

# Run with specific report format
atest run -p testsuite.yaml --report md --report-file report.md

# Generate sample test suite
atest sample

# Start server mode with web UI
atest server --port 7070 --http-port 8080

# Create mock server
atest mock -p testsuite.yaml --port 9090

# Convert tests to JMeter
atest convert -p testsuite.yaml --converter jmeter -t output.jmx

# Install as service
atest service install
```

## Test Suite Properties

### Suite Level

- `name`: Suite name
- `api`: Base API URL (supports templates: `{{default "http://localhost:8080" (env "SERVER")}}`)
- `param`: Global parameters available in all tests
- `spec`: Protocol specification (for gRPC/GraphQL)
- `items`: Array of test cases

### Test Case Level

**Request:**
- `name`: Test case name
- `request.api`: Endpoint path
- `request.method`: HTTP method (GET, POST, PUT, DELETE, etc.)
- `request.header`: Request headers
- `request.body`: Request body (supports templates)
- `request.cookie`: Cookies to send
- `request.url`: Full URL (overrides `api` + `api` combination)
- `request.form`: Form data
- `request.files`: File uploads

**Expect:**
- `expect.statusCode`: Expected HTTP status code
- `expect.body`: Expected response body
- `expect.bodyFieldsExpect`: Expected field values
- `expect.schema`: JSON schema for validation
- `expect.verify`: Array of verification expressions
- `expect.verifyWithSelector`: Verification with JSONPath
- `expect.contentType`: Expected content type

**Control:**
- `before.items`: Commands to run before test
- `after.items`: Commands to run after test
- `cond`: Conditional execution

## gRPC Testing

```yaml
name: grpc-sample
api: 127.0.0.1:7070
spec:
  kind: grpc
  rpc:
    import:
      - ./path/to/proto/files
    protofile: service.proto
items:
  - name: UnaryCall
    request:
      api: /service.Service/Method
      body: |
        {"field": "value"}
  - name: ServerStream
    request:
      api: /service.Service/StreamMethod
  - name: ClientStream
    request:
      api: /service.Service/ClientStream
      body: |
        [{"msg": "msg1"}, {"msg": "msg2"}]
```

## Template Functions

Available Sprig functions plus custom:
- `randAlpha n`: Generate random alphabetic string
- `randNumeric n`: Generate random numeric string
- `randASCII n`: Generate random ASCII string
- `env "VAR"`: Get environment variable
- `default "value" (env "VAR")`: Default value
- `int64 value`: Convert to int64
- `index .array 0`: Get array element

## Verification Examples

```yaml
expect:
  verify:
    - data.status == "success"
    - len(data.items) > 0
    - data.error == nil
    - data.code in [200, 201]
    - data.message startsWith "OK"
    - contains(data.tags, "important")
```

## Load Testing Patterns

```bash
# Duration-based
atest run -p testsuite.yaml --duration 5m

# Thread-based (concurrent users)
atest run -p testsuite.yaml --thread 10

# QPS-based (requests per second)
atest run -p testsuite.yaml --qps 100

# Combined
atest run -p testsuite.yaml --duration 5m --thread 5 --qps 50
```

## Mock Server

```bash
# Start mock server from test suite
atest mock -p testsuite.yaml --port 9090

# Mock with OpenAPI spec
atest mock --swagger-url https://api.example.com/swagger.json --port 9090
```

## Data Sources

Test suites can be loaded from:
- Local files: `-p testsuite.yaml`
- Git: `git://github.com/user/repo//path/to/suite.yaml`
- HTTP/HTTPS: `https://example.com/suite.yaml`
- S3: `s3://bucket/path/suite.yaml`
- Database: `mysql://user:pass@host/db`
- Etcd: `etcd://host:port/key`

## Best Practices

1. **Use descriptive test names**: `createUser`, `getProjectById`
2. **Parametrize common values**: Use `param` section for shared data
3. **Chain tests**: Use response data in subsequent tests via `data.field`
4. **Add verification**: Always verify critical response fields
5. **Handle errors**: Use `request.ignoreError` for intentional failure tests
6. **Use templates**: Leverage template functions for dynamic data
7. **Organize suites**: Group related tests in separate suites

## Debugging Tips

1. **Run single test**: `atest run -p suite.yaml testCaseName`
2. **Enable verbose output**: Check logs for detailed request/response
3. **Use JSON report**: `--report json` for machine-readable output
4. **Test with curl**: Verify API works independently before writing tests
5. **Check schema validation**: Ensure `expect.schema` matches actual response
6. **Verify template syntax**: Template errors show at runtime

## Common Issues

- **Port already in use**: Server port conflict, use different port
- **Connection refused**: API server not running or wrong URL
- **Template not rendered**: Check template syntax and variable names
- **Verification failed**: Check field paths in `data.` expressions
- **Proto file not found**: Verify `spec.rpc.import` paths are correct

## Related Files

- Test suites: `*.yaml` files with test definitions
- Sample: Run `atest sample` to generate a sample suite
- Documentation: https://github.com/LinuxSuRen/api-testing
- Schema: https://linuxsuren.github.io/api-testing/api-testing-schema.json
