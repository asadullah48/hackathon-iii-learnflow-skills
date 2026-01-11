---
name: agents-md-gen
description: Generate comprehensive AGENTS.md files for repositories
---

# Agents.md Generator

## When to Use
- Create AGENTS.md documentation for AI agents
- Document project structure for Claude Code/Goose

## Instructions

Run: `python scripts/generate_agents_md.py <project_path> [project_type]`

Project types: fastapi, nextjs, microservices, k8s, fullstack (auto-detected)

## Outputs
- AGENTS.md file in project root
- Project structure documentation
