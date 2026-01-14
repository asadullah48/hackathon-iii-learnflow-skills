# MCP Code Execution - Reference Documentation

## Architecture Overview

Provides secure code execution environments for Python and JavaScript with output capture and error handling.
````
┌─────────────────────────────────────────┐
│  Code Execution Engine                  │
│  ┌───────────────────────────────────┐ │
│  │  Python Executor (exec.py)        │ │
│  │  - subprocess isolation           │ │
│  │  - timeout protection (30s)       │ │
│  │  - stdout/stderr capture          │ │
│  │  - resource limits                │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  JavaScript Executor (exec.js)    │ │
│  │  - Node.js child_process          │ │
│  │  - timeout protection (30s)       │ │
│  │  - console.log capture            │ │
│  │  - error handling                 │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
````

## Use Cases

### 1. Student Code Validation
Execute student submissions and verify correctness:
````python
# Student code
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""

# Execute and check output
result = execute_python(code, timeout=5)
assert result['output'].strip() == '55'
````

### 2. Auto-Grading System
Test submissions against test cases:
````python
code_template = """
{student_code}

# Test cases
assert sum_list([1,2,3]) == 6
assert sum_list([]) == 0
assert sum_list([-1,1]) == 0
print("All tests passed!")
"""

result = execute_python(code_template.format(student_code=submission))
grade = 100 if "All tests passed" in result['output'] else 0
````

### 3. Interactive REPL
Support live coding sessions:
````javascript
// Execute JavaScript snippets
const code = `
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
console.log(doubled);
`;

const result = await executeJavaScript(code);
// Output: [2, 4, 6, 8, 10]
````

### 4. Code Explanation
Generate examples for concepts:
````python
concept = "list comprehensions"
example_code = """
# Traditional loop
squares = []
for i in range(10):
    squares.append(i**2)

# List comprehension
squares = [i**2 for i in range(10)]
print(squares)
"""

result = execute_python(example_code)
# Shows both approaches produce same output
````

## Script Reference

### exec.py - Python Execution
````bash
python scripts/exec.py <code-file> [--timeout=30]
````

**Direct Invocation:**
````python
from exec import execute_python

result = execute_python(
    code="print('Hello, World!')",
    timeout=10  # seconds
)

print(result)
# {
#   'output': 'Hello, World!\n',
#   'error': None,
#   'exit_code': 0,
#   'execution_time': 0.05
# }
````

**Security Features:**
- Process isolation
- Timeout enforcement
- No file system access
- No network access
- Resource limits (CPU/memory)

**Limitations:**
- Cannot import external packages (only stdlib)
- No GUI operations
- No multiprocessing
- No file I/O outside /tmp

### exec.js - JavaScript Execution
````bash
node scripts/exec.js <code-file> [--timeout=30]
````

**Direct Invocation:**
````javascript
const { executeJavaScript } = require('./exec');

const result = await executeJavaScript(`
  const factorial = n => n <= 1 ? 1 : n * factorial(n - 1);
  console.log(factorial(5));
`, { timeout: 10000 });

console.log(result);
// {
//   output: '120\n',
//   error: null,
//   exitCode: 0,
//   executionTime: 45
// }
````

**Security Features:**
- V8 isolate
- Timeout enforcement
- No require() for file system modules
- No process.exit()
- Memory limits

**Allowed Built-ins:**
- console.log/error/warn
- Math, Date, JSON
- Array, Object, String methods
- setTimeout/setInterval (with timeout enforcement)

## Advanced Usage

### Custom Test Runners
````python
def run_tests(student_code: str, test_cases: list) -> dict:
    """Execute code with multiple test cases."""
    results = []
    
    for i, test in enumerate(test_cases):
        code = f"{student_code}\n\n{test['code']}"
        result = execute_python(code, timeout=5)
        
        passed = test['expected'] in result['output']
        results.append({
            'test': i + 1,
            'passed': passed,
            'output': result['output'],
            'expected': test['expected']
        })
    
    return {
        'total': len(test_cases),
        'passed': sum(1 for r in results if r['passed']),
        'results': results
    }
````

### Syntax Validation
````python
import ast

def validate_syntax(code: str) -> dict:
    """Check Python syntax before execution."""
    try:
        ast.parse(code)
        return {'valid': True, 'error': None}
    except SyntaxError as e:
        return {
            'valid': False,
            'error': str(e),
            'line': e.lineno,
            'offset': e.offset
        }

# Usage
validation = validate_syntax(student_code)
if validation['valid']:
    result = execute_python(student_code)
else:
    return {'error': validation['error']}
````

### Output Comparison
````python
def compare_outputs(code1: str, code2: str) -> bool:
    """Check if two implementations produce same output."""
    result1 = execute_python(code1)
    result2 = execute_python(code2)
    
    return (
        result1['output'] == result2['output'] and
        result1['exit_code'] == 0 and
        result2['exit_code'] == 0
    )
````

### Progress Tracking
````python
def execute_with_progress(code: str, checkpoints: list) -> dict:
    """Execute code and track variable values at checkpoints."""
    instrumented_code = code
    
    for checkpoint in checkpoints:
        instrumented_code = instrumented_code.replace(
            checkpoint,
            f"{checkpoint}\nprint(f'CHECKPOINT:{checkpoint}={{locals()}}')"
        )
    
    result = execute_python(instrumented_code)
    
    # Parse checkpoint outputs
    progress = {}
    for line in result['output'].split('\n'):
        if line.startswith('CHECKPOINT:'):
            name, values = line.split(':', 1)[1].split('=', 1)
            progress[name] = eval(values)
    
    return progress
````

## Error Handling

### Timeout Errors
````python
result = execute_python("""
while True:
    pass  # Infinite loop
""", timeout=5)

# result = {
#   'output': '',
#   'error': 'TimeoutExpired: Code execution exceeded 5 seconds',
#   'exit_code': -1,
#   'execution_time': 5.0
# }
````

### Runtime Errors
````python
result = execute_python("""
x = 1 / 0  # Division by zero
""")

# result = {
#   'output': '',
#   'error': 'ZeroDivisionError: division by zero',
#   'exit_code': 1,
#   'execution_time': 0.02
# }
````

### Import Errors
````python
result = execute_python("""
import requests  # Not available
""")

# result = {
#   'output': '',
#   'error': 'ModuleNotFoundError: No module named "requests"',
#   'exit_code': 1,
#   'execution_time': 0.03
# }
````

## Security Considerations

### Input Sanitization
````python
def sanitize_code(code: str) -> str:
    """Remove dangerous operations."""
    dangerous_patterns = [
        'import os',
        'import sys',
        'import subprocess',
        '__import__',
        'eval(',
        'exec(',
        'compile(',
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            raise ValueError(f"Forbidden pattern: {pattern}")
    
    return code
````

### Resource Limits
````python
import resource

def set_resource_limits():
    """Limit CPU and memory usage."""
    # Max 10 seconds CPU time
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    
    # Max 256MB memory
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
````

### Sandboxing (Docker)
````dockerfile
FROM python:3.11-alpine
WORKDIR /sandbox
COPY exec.py .
RUN adduser -D sandbox
USER sandbox
CMD ["python", "exec.py"]
````
````bash
# Run in container
docker run --rm \
  --cpus=0.5 \
  --memory=256m \
  --network=none \
  -v $(pwd)/code.py:/sandbox/code.py:ro \
  sandbox-image python exec.py /sandbox/code.py
````

## Integration Examples

### FastAPI Endpoint
````python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class CodeRequest(BaseModel):
    code: str
    language: str
    timeout: int = 30

@app.post("/execute")
async def execute_code(request: CodeRequest):
    try:
        if request.language == "python":
            result = execute_python(request.code, timeout=request.timeout)
        elif request.language == "javascript":
            result = execute_javascript(request.code, timeout=request.timeout)
        else:
            raise HTTPException(400, "Unsupported language")
        
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
````

### Dapr State Integration
````python
from dapr.clients import DaprClient

def save_execution_result(user_id: str, result: dict):
    """Store execution history in Dapr state."""
    with DaprClient() as client:
        client.save_state(
            store_name="statestore",
            key=f"executions:{user_id}",
            value=result
        )
````

### Kafka Event Publishing
````python
from dapr.clients import DaprClient

def publish_execution_event(result: dict):
    """Notify other services of code execution."""
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="pubsub",
            topic_name="code.executed",
            data={
                'user_id': result['user_id'],
                'passed': result['exit_code'] == 0,
                'execution_time': result['execution_time']
            }
        )
````

## Performance Optimization

### Code Caching
````python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def execute_cached(code_hash: str, code: str) -> dict:
    """Cache execution results for identical code."""
    return execute_python(code)

def execute_with_cache(code: str) -> dict:
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    return execute_cached(code_hash, code)
````

### Parallel Execution
````python
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_batch(code_list: list) -> list:
    """Execute multiple code snippets in parallel."""
    results = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(execute_python, code): i 
            for i, code in enumerate(code_list)
        }
        
        for future in as_completed(futures):
            idx = futures[future]
            results.append((idx, future.result()))
    
    # Sort by original order
    return [r for _, r in sorted(results)]
````

## References

- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [Node.js child_process](https://nodejs.org/api/child_process.html)
- [Code Sandboxing Best Practices](https://owasp.org/www-community/vulnerabilities/Code_Injection)
- [V8 Isolates](https://v8.dev/docs/embed#isolates)
