"""
MCP Server entry point
"""

import sys
from .server import main

if __name__ == "__main__":
    sys.exit(main())  # type: ignore[call-arg]
