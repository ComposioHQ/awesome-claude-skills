---
name: api-documentation-generator
description: Generate comprehensive API documentation from code comments, type definitions, and OpenAPI specs. Use when creating or updating API docs.
---

# API Documentation Generator

Automatically generates comprehensive API documentation from various sources including code comments, TypeScript interfaces, function signatures, and existing OpenAPI specifications. Ensures documentation stays synchronized with code changes.

## When to Use This Skill

- Creating API documentation for new endpoints or services
- Updating existing docs when code changes
- Converting code types to OpenAPI specifications
- Generating client SDK documentation
- Creating Postman collections from code

## What This Skill Does

1. **Code Analysis**: Extracts API information from source code comments, JSDoc, and type definitions
2. **OpenAPI Generation**: Creates or updates OpenAPI/Swagger specifications
3. **Markdown Documentation**: Generates human-readable API reference docs
4. **Client SDK Docs**: Creates documentation for API client libraries
5. **Collection Export**: Exports Postman/Insomnia collections

## How to Use

### Basic Usage

```
Generate API documentation from this Express.js route file
```

### Advanced Usage

```
Create OpenAPI 3.0 spec from these TypeScript interfaces and generate Markdown docs with examples
```

## Example

**User**: "Generate API docs for this FastAPI endpoint"

**Input**:
```python
@app.post("/users/{user_id}/orders")
async def create_order(user_id: int, order: OrderCreate):
    """Create a new order for a user.
    
    Args:
        user_id: The ID of the user
        order: Order creation data
        
    Returns:
        Created order with ID and timestamp
    """
    ...
```

**Output**:
```yaml
# OpenAPI snippet
/users/{user_id}/orders:
  post:
    summary: Create a new order for a user
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OrderCreate'
    responses:
      200:
        description: Created order with ID and timestamp
```

**Inspired by:** Swagger Codegen and Stoplight Studio workflows

## Tips

- Include JSDoc/JavaDoc comments for best results
- Provide example request/response data when possible
- Specify output format preference (OpenAPI, Markdown, Postman)
- Review generated security schemas carefully

## Common Use Cases

- Documenting REST API endpoints from backend code
- Keeping API docs in sync with code changes
- Creating API reference for microservices
- Generating client libraries documentation
- Building developer portal content
