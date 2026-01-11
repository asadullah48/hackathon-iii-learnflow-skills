---
name: mcp-code-execution
description: Execute code snippets via MCP server with zero-token script pattern
---

# MCP Code Execution

## When to Use
- Run Python/Node.js code without writing files
- Quick calculations, validations, or transformations
- Zero-token execution pattern (no script files needed)

## Instructions

1. **Python**: `python scripts/exec.py "print(2+2)"`
2. **Node.js**: `node scripts/exec.js "console.log(2+2)"`

## Outputs
- Direct stdout/stderr
- Exit code (0 = success, 1 = error)
