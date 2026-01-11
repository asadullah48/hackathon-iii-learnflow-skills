#!/usr/bin/env python3
import sys
try:
    exec(sys.argv[1] if len(sys.argv) > 1 else "")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
